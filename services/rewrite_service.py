"""
rewrite_service.py
------------------
Orchestrates the core rewrite operation:
  - Builds the prompt
  - Calls the Grok API
  - Returns structured result with a change summary
"""

from typing import Optional
from services.grok_client import chat_completion
from prompts.rewrite_prompt import (
    REWRITE_SYSTEM_PROMPT,
    build_rewrite_user_prompt,
)


def rewrite_text(
    original_text: str,
    tone: str,
    audience: str,
    length_pct: int,
    formality: int,
) -> str:
    """
    Rewrite ``original_text`` using the Grok API with the given parameters.

    Args:
        original_text: Raw text provided by the user.
        tone:          Target tone (e.g. 'Formal', 'Casual').
        audience:      Target audience (e.g. 'Children', 'Executives').
        length_pct:    Desired output length as % of input length (20–150).
        formality:     Formality score 0–100.

    Returns:
        The rewritten text as a plain string.
    """
    user_prompt = build_rewrite_user_prompt(
        original_text=original_text,
        tone=tone,
        audience=audience,
        length_pct=length_pct,
        formality=formality,
    )
    return chat_completion(
        system_prompt=REWRITE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=2048,
    )


def build_change_summary(
    original_tone: Optional[str],
    tone: str,
    audience: str,
    length_pct: int,
    formality: int,
) -> list[str]:
    """
    Generate a human-readable bullet list describing what was changed.

    Args:
        original_tone: If provided, the previous tone (used to show change).
        tone:          The newly applied tone.
        audience:      The target audience chosen.
        length_pct:    Length percentage (relative to original).
        formality:     Formality score 0–100.

    Returns:
        A list of change-summary strings (each prefixed with ✓).
    """
    summary: list[str] = []

    summary.append(f"✓ Tone changed to **{tone}**")
    summary.append(f"✓ Audience adapted for **{audience}**")

    # Formality description
    if formality >= 70:
        summary.append("✓ Formality **increased** to a high level")
    elif formality <= 30:
        summary.append("✓ Formality **decreased** to a casual level")
    else:
        summary.append("✓ Formality kept at a **balanced** level")

    # Length description
    if length_pct < 80:
        summary.append(f"✓ Length **shortened** to ~{length_pct}% of original")
    elif length_pct > 120:
        summary.append(f"✓ Length **expanded** to ~{length_pct}% of original")
    else:
        summary.append(f"✓ Length kept **approximately the same** (~{length_pct}%)")

    summary.append("✓ Grammar and readability **improved**")

    return summary


# ---------------------------------------------------------------------------
# Multi-tone generation
# ---------------------------------------------------------------------------

ALL_TONES: list[dict] = [
    {"tone": "Formal",            "emoji": "🎩"},
    {"tone": "Casual",            "emoji": "😊"},
    {"tone": "Child-Friendly",    "emoji": "🧒"},
    {"tone": "Executive Summary", "emoji": "📊"},
]


def generate_all_tones(
    original_text: str,
    audience: str,
    length_pct: int,
    formality: int,
) -> list[dict]:
    """
    Generate rewrites for all four preset tones sequentially.

    Args:
        original_text: The source text to rewrite.
        audience:      Target audience applied to all rewrites.
        length_pct:    Desired length percentage for all rewrites.
        formality:     Formality score applied to all rewrites.

    Returns:
        A list of dicts, each with keys: ``tone``, ``emoji``, ``text``.
        If a rewrite fails, ``text`` is set to an error message string.
    """
    results: list[dict] = []
    for entry in ALL_TONES:
        try:
            rewritten = rewrite_text(
                original_text=original_text,
                tone=entry["tone"],
                audience=audience,
                length_pct=length_pct,
                formality=formality,
            )
            results.append({**entry, "text": rewritten})
        except Exception as exc:  # noqa: BLE001
            results.append({**entry, "text": f"⚠️ Error: {exc}"})
    return results
