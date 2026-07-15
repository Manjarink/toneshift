"""
grok_client.py
--------------
Thin wrapper around the Groq API (OpenAI-compatible endpoint).
All API calls in the application go through this module.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
DEFAULT_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _get_client() -> OpenAI:
    """
    Build and return an OpenAI-compatible client pointed at Groq's endpoint.

    Raises:
        EnvironmentError: If GROQ_API_KEY is not set.
    """
    api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Please add it to your .env file or environment variables."
        )
    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    model: Optional[str] = None,
) -> str:
    """
    Send a chat-completion request to the Groq API and return the text response.

    Args:
        system_prompt: Instruction context for the model.
        user_prompt:   The actual user message / content to process.
        temperature:   Sampling temperature (0 = deterministic, 1 = creative).
        max_tokens:    Upper bound on response length.
        model:         Override the default model name.

    Returns:
        The model's text response as a plain string.

    Raises:
        EnvironmentError: Propagated from _get_client if key is missing.
        RuntimeError:     On unexpected API errors.
    """
    client = _get_client()
    selected_model = model or DEFAULT_MODEL

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Groq API returned an empty response.")
    return content.strip()
