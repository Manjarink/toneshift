"""
rewrite_prompt.py
-----------------
Builds the system and user prompts used for the rewrite feature.
"""

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
REWRITE_SYSTEM_PROMPT: str = (
    "You are ToneShift, an expert writing assistant that rewrites text for "
    "different audiences and communication styles. "
    "You always preserve the original meaning exactly — never invent facts, "
    "never remove important information, and never add new claims. "
    "Your only task is to adapt wording, tone, structure, and style."
)


def build_rewrite_user_prompt(
    original_text: str,
    tone: str,
    audience: str,
    length_pct: int,
    formality: int,
) -> str:
    """
    Construct the user-facing rewrite prompt dynamically.

    Args:
        original_text: The raw text the user wants rewritten.
        tone:          Selected tone (e.g. 'Formal', 'Casual').
        audience:      Target audience (e.g. 'Children', 'Executives').
        length_pct:    Desired output length as percentage of input (20–150).
        formality:     Formality level 0–100 (0 = very casual, 100 = very formal).

    Returns:
        A fully formed prompt string ready to send to the API.
    """
    formality_label = _formality_label(formality)
    length_instruction = _length_instruction(length_pct)

    return (
        f"Rewrite the following text according to these exact requirements:\n\n"
        f"• Tone: {tone}\n"
        f"• Target Audience: {audience}\n"
        f"• Length: {length_instruction} (target ~{length_pct}% of the original length)\n"
        f"• Formality Level: {formality}/100 ({formality_label})\n\n"
        f"Rules you MUST follow:\n"
        f"  1. Preserve the original meaning completely — do NOT invent or omit facts.\n"
        f"  2. Adapt wording and vocabulary to suit the '{audience}' audience.\n"
        f"  3. Match the '{tone}' tone throughout the entire text.\n"
        f"  4. Improve grammar and readability where possible.\n"
        f"  5. Output ONLY the rewritten text — no preamble, no explanation.\n\n"
        f"Original Text:\n\"\"\"\n{original_text}\n\"\"\""
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _formality_label(formality: int) -> str:
    """Map a 0–100 formality score to a human-readable label."""
    if formality <= 20:
        return "very casual / conversational"
    elif formality <= 40:
        return "casual"
    elif formality <= 60:
        return "neutral / balanced"
    elif formality <= 80:
        return "formal"
    else:
        return "very formal / academic"


def _length_instruction(length_pct: int) -> str:
    """Describe the desired length relative to the original."""
    if length_pct < 50:
        return f"significantly shorter (~{length_pct}% of original)"
    elif length_pct < 90:
        return f"shorter (~{length_pct}% of original)"
    elif length_pct <= 110:
        return f"approximately the same length (~{length_pct}% of original)"
    elif length_pct <= 130:
        return f"slightly longer (~{length_pct}% of original)"
    else:
        return f"considerably longer (~{length_pct}% of original)"
