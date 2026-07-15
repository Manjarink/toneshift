"""
back_translation.py
-------------------
Handles the back-translation step:
sends the rewritten text to Grok and returns a neutral-English version
for meaning-drift comparison.
"""

from services.grok_client import chat_completion
from prompts.back_translation_prompt import (
    BACK_TRANSLATION_SYSTEM_PROMPT,
    build_back_translation_user_prompt,
)


def back_translate(rewritten_text: str) -> str:
    """
    Back-translate ``rewritten_text`` into neutral, plain English.

    This strips away tone/style while preserving all factual content,
    producing a version that can be semantically compared to the original.

    Args:
        rewritten_text: The tone-adapted text produced by the rewrite step.

    Returns:
        A plain-English back-translation string.
    """
    user_prompt = build_back_translation_user_prompt(rewritten_text)
    return chat_completion(
        system_prompt=BACK_TRANSLATION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,   # Low temperature for faithful reproduction
        max_tokens=2048,
    )
