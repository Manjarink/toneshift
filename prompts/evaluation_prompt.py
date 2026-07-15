"""
evaluation_prompt.py
--------------------
Prompt used to ask Grok to compare the original text with the
back-translated text and return a structured JSON verdict.
"""

EVALUATION_SYSTEM_PROMPT: str = (
    "You are a semantic similarity evaluator. "
    "You compare two texts and determine whether they convey the same meaning. "
    "You respond ONLY with a valid JSON object — no markdown, no explanation, "
    "no extra text."
)

EXPECTED_JSON_SCHEMA: str = """{
  "meaning_preserved": <true | false>,
  "confidence": <integer 0-100>,
  "missing_information": [<list of strings, or empty list>],
  "added_information": [<list of strings, or empty list>],
  "verdict": "<one-sentence summary>"
}"""


def build_evaluation_user_prompt(original_text: str, back_translated_text: str) -> str:
    """
    Build the user prompt for the meaning-verification evaluation.

    Args:
        original_text:        The user's original input text.
        back_translated_text: The neutral back-translation produced in the prior step.

    Returns:
        A prompt string requesting a JSON comparison result.
    """
    return (
        "Compare the two texts below and determine whether they convey the same meaning.\n\n"
        f"--- ORIGINAL TEXT ---\n\"\"\"\n{original_text}\n\"\"\"\n\n"
        f"--- BACK-TRANSLATED TEXT ---\n\"\"\"\n{back_translated_text}\n\"\"\"\n\n"
        f"Return ONLY a JSON object in exactly this format:\n{EXPECTED_JSON_SCHEMA}\n\n"
        "Be strict: list any missing or added facts, even minor ones."
    )
