"""
back_translation_prompt.py
--------------------------
Prompt used to back-translate the rewritten text into neutral English,
so we can compare it against the original and detect meaning drift.
"""

BACK_TRANSLATION_SYSTEM_PROMPT: str = (
    "You are a neutral translation assistant. "
    "Your sole task is to rewrite text into plain, simple, neutral English "
    "while preserving every single detail and piece of information exactly as given. "
    "Do NOT simplify meaning, omit facts, or add anything new. "
    "Remove any stylistic flourishes, jargon, or audience-specific phrasing, "
    "but keep ALL the information intact."
)


def build_back_translation_user_prompt(rewritten_text: str) -> str:
    """
    Build the user prompt for back-translation.

    Args:
        rewritten_text: The tone-adapted text produced by the rewrite step.

    Returns:
        A prompt string requesting neutral-English back-translation.
    """
    return (
        "Rewrite the following text into plain, neutral English. "
        "Preserve every detail and fact exactly. "
        "Output ONLY the neutralised text — no explanation.\n\n"
        f"Text to neutralise:\n\"\"\"\n{rewritten_text}\n\"\"\""
    )
