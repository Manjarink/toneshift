"""
evaluation_service.py
---------------------
Calls Grok to compare the original text and back-translated text,
then parses and returns a structured JSON verdict about meaning preservation.
"""

import json
import re
from typing import Any

from services.grok_client import chat_completion
from prompts.evaluation_prompt import (
    EVALUATION_SYSTEM_PROMPT,
    build_evaluation_user_prompt,
)

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
EvaluationResult = dict[str, Any]

# Default result returned when evaluation fails
_FALLBACK_RESULT: EvaluationResult = {
    "meaning_preserved": False,
    "confidence": 0,
    "missing_information": [],
    "added_information": [],
    "verdict": "Evaluation could not be completed due to an API or parsing error.",
}


def evaluate_meaning(original_text: str, back_translated_text: str) -> EvaluationResult:
    """
    Ask Grok to semantically compare ``original_text`` with ``back_translated_text``.

    Args:
        original_text:        The user's original, unmodified input.
        back_translated_text: The neutral back-translation of the rewritten output.

    Returns:
        A dict with keys:
          - meaning_preserved (bool)
          - confidence (int, 0–100)
          - missing_information (list[str])
          - added_information (list[str])
          - verdict (str)
        Falls back to ``_FALLBACK_RESULT`` on any error.
    """
    user_prompt = build_evaluation_user_prompt(
        original_text=original_text,
        back_translated_text=back_translated_text,
    )

    raw_response = chat_completion(
        system_prompt=EVALUATION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.0,   # Deterministic for structured output
        max_tokens=1024,
    )

    return _parse_evaluation_response(raw_response)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _parse_evaluation_response(raw: str) -> EvaluationResult:
    """
    Extract and parse the JSON object from the model's raw response.

    Handles cases where the model wraps JSON in markdown code fences.

    Args:
        raw: The raw string returned by the API.

    Returns:
        Parsed dict matching the expected schema, or ``_FALLBACK_RESULT``.
    """
    # Strip markdown fences if present
    cleaned = raw.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", cleaned)
    if fenced:
        cleaned = fenced.group(1)

    # Also try to extract a bare JSON object
    json_match = re.search(r"\{[\s\S]+\}", cleaned)
    if json_match:
        cleaned = json_match.group(0)

    try:
        parsed: dict = json.loads(cleaned)
    except json.JSONDecodeError:
        return {**_FALLBACK_RESULT, "verdict": f"JSON parse error. Raw response: {raw[:200]}"}

    # Normalise and validate fields
    result: EvaluationResult = {
        "meaning_preserved": bool(parsed.get("meaning_preserved", False)),
        "confidence": int(parsed.get("confidence", 0)),
        "missing_information": list(parsed.get("missing_information", [])),
        "added_information": list(parsed.get("added_information", [])),
        "verdict": str(parsed.get("verdict", "No verdict provided.")),
    }

    # Clamp confidence to [0, 100]
    result["confidence"] = max(0, min(100, result["confidence"]))

    return result
