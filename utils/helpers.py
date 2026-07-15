"""
helpers.py
----------
Miscellaneous helper functions used across the ToneShift application.
"""

import re


def word_count(text: str) -> int:
    """
    Return the number of words in ``text``.

    Args:
        text: Any string input.

    Returns:
        Integer word count (0 for empty / whitespace-only input).
    """
    return len(text.split()) if text.strip() else 0


def char_count(text: str) -> int:
    """
    Return the number of characters in ``text`` (excluding leading/trailing whitespace).

    Args:
        text: Any string input.

    Returns:
        Integer character count.
    """
    return len(text.strip())


def reading_time_seconds(text: str, wpm: int = 200) -> int:
    """
    Estimate reading time in seconds given an average reading speed.

    Args:
        text: Input text.
        wpm:  Words per minute (default 200 — average adult reader).

    Returns:
        Estimated seconds to read the text (minimum 1 second).
    """
    words = word_count(text)
    seconds = max(1, round((words / wpm) * 60))
    return seconds


def format_reading_time(text: str) -> str:
    """
    Format reading time as a human-readable string.

    Args:
        text: Input text.

    Returns:
        e.g. "< 1 min read" or "3 min read".
    """
    seconds = reading_time_seconds(text)
    minutes = round(seconds / 60)
    if minutes < 1:
        return "< 1 min read"
    return f"{minutes} min read"


def truncate_text(text: str, max_chars: int = 5000) -> str:
    """
    Truncate text to ``max_chars`` characters, appending an ellipsis.

    Args:
        text:      Input text.
        max_chars: Maximum allowed character count.

    Returns:
        Truncated string ending in '...' if the input exceeded the limit.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def sanitize_filename(name: str) -> str:
    """
    Strip characters from ``name`` that are invalid in filenames.

    Args:
        name: Proposed file name (without extension).

    Returns:
        A safe filename string.
    """
    safe = re.sub(r'[^\w\s\-]', '', name)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe or "toneshift_export"


def validate_api_key_format(key: str) -> bool:
    """
    Perform a basic sanity check on the xAI API key format.

    xAI keys typically begin with 'xai-' followed by alphanumeric characters.

    Args:
        key: The API key string to validate.

    Returns:
        True if the format looks plausible, False otherwise.
    """
    return bool(key and re.match(r'^xai-[A-Za-z0-9]{20,}$', key.strip()))


def confidence_color(confidence: int) -> str:
    """
    Map a confidence score to a CSS colour string for UI styling.

    Args:
        confidence: Integer 0–100.

    Returns:
        A hex colour string.
    """
    if confidence >= 90:
        return "#22c55e"   # green-500
    elif confidence >= 70:
        return "#f97316"   # orange-500
    else:
        return "#ef4444"   # red-500


def confidence_label(confidence: int) -> str:
    """
    Return a human-readable confidence label.

    Args:
        confidence: Integer 0–100.

    Returns:
        Label string.
    """
    if confidence >= 90:
        return "High Confidence"
    elif confidence >= 70:
        return "Medium Confidence"
    else:
        return "Low Confidence — Possible Meaning Drift"
