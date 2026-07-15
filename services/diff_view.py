"""
diff_view.py
------------
Generates an HTML side-by-side diff between two texts using
Python's built-in difflib.HtmlDiff.
"""

import difflib
from typing import Optional


def generate_html_diff(
    original_text: str,
    rewritten_text: str,
    original_label: str = "Original",
    rewritten_label: str = "Rewritten",
    context: bool = True,
    num_lines: int = 3,
) -> str:
    """
    Produce a styled HTML diff table comparing two texts word-by-word.

    Splits each text into words (joined with newlines) so the diff highlights
    individual word additions, removals, and changes rather than entire lines.

    Args:
        original_text:  The user's original input text.
        rewritten_text: The AI-rewritten version.
        original_label: Column header for the left (original) side.
        rewritten_label: Column header for the right (rewritten) side.
        context:        If True, only context lines around changes are shown.
        num_lines:      Number of context lines to show around each change.

    Returns:
        A complete HTML string containing the diff table, with inline CSS
        wrapping so it can be embedded directly in a Streamlit st.html() call.
    """
    # Split into sentences / lines for a readable diff
    original_lines = _split_for_diff(original_text)
    rewritten_lines = _split_for_diff(rewritten_text)

    diff_html = difflib.HtmlDiff(
        wrapcolumn=80,
        tabsize=4,
    ).make_file(
        fromlines=original_lines,
        tolines=rewritten_lines,
        fromdesc=original_label,
        todesc=rewritten_label,
        context=context,
        numlines=num_lines,
    )

    # Inject overrides so it looks good inside Streamlit
    diff_html = _inject_custom_styles(diff_html)
    return diff_html


def generate_inline_diff_table(original_text: str, rewritten_text: str) -> str:
    """
    Produce a compact unified diff (table-only, no full HTML page) suitable
    for embedding inside an existing HTML layout.

    Args:
        original_text:  The user's original input text.
        rewritten_text: The AI-rewritten version.

    Returns:
        An HTML string containing just the ``<table>`` diff element.
    """
    original_lines = _split_for_diff(original_text)
    rewritten_lines = _split_for_diff(rewritten_text)

    table_html: str = difflib.HtmlDiff(wrapcolumn=80).make_table(
        fromlines=original_lines,
        tolines=rewritten_lines,
        fromdesc="Original",
        todesc="Rewritten",
        context=True,
        numlines=3,
    )
    return table_html


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _split_for_diff(text: str) -> list[str]:
    """
    Split text into individual lines, preserving paragraph breaks.

    Uses sentence-boundary splitting ('. ', '! ', '? ') to make diffs
    more readable at a sentence level.

    Args:
        text: Raw input string.

    Returns:
        A list of non-empty line strings.
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        # Break at sentence boundaries
        import re
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        lines.extend(s.strip() for s in sentences if s.strip())
    return lines


def _inject_custom_styles(html: str) -> str:
    """
    Inject custom CSS into the difflib-generated HTML to make it
    look clean and modern inside Streamlit's dark/light themes.

    Args:
        html: Raw HTML string from difflib.HtmlDiff.

    Returns:
        HTML string with additional CSS injected into the <head>.
    """
    custom_css = """
<style>
  body { background: transparent !important; font-family: 'Inter', sans-serif; }
  table.diff {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
  }
  table.diff th {
    background: #1e293b;
    color: #94a3b8;
    padding: 8px 12px;
    text-align: center;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  table.diff td {
    padding: 4px 10px;
    vertical-align: top;
    border: 1px solid #334155;
    line-height: 1.6;
  }
  .diff_header { background: #0f172a; color: #64748b !important; }
  .diff_next   { background: #0f172a; }
  td.diff_add  { background: #14532d66; color: #86efac; }
  td.diff_chg  { background: #78350f66; color: #fcd34d; }
  td.diff_sub  { background: #7f1d1d66; color: #fca5a5; }
  span.diff_add { background: #15803d; color: #dcfce7; border-radius: 2px; padding: 0 2px; }
  span.diff_chg { background: #b45309; color: #fef3c7; border-radius: 2px; padding: 0 2px; }
  span.diff_sub { background: #b91c1c; color: #fee2e2; border-radius: 2px; padding: 0 2px;
                  text-decoration: line-through; }
  .diff_header a { color: #60a5fa; }
</style>
"""
    return html.replace("</head>", custom_css + "\n</head>", 1)
