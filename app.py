"""
app.py
------
ToneShift: Audience-Aware Rewriter
A production-grade Streamlit application that rewrites text for different
audiences and tones using the Grok API, with back-translation meaning verification.
"""

import os
import sys
import json

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path setup — ensures subpackages resolve correctly
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))
load_dotenv()

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
from services.rewrite_service import rewrite_text, build_change_summary, generate_all_tones
from services.back_translation import back_translate
from services.evaluation_service import evaluate_meaning
from services.diff_view import generate_html_diff
from utils.export import export_txt, export_pdf
from utils.helpers import (
    word_count,
    char_count,
    format_reading_time,
    confidence_color,
    confidence_label,
    validate_api_key_format,
)

# ===========================================================================
# Page config — must be first Streamlit call
# ===========================================================================
st.set_page_config(
    page_title="ToneShift — Audience-Aware Rewriter",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================================================
# Global CSS
# ===========================================================================
st.markdown(
    """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a0f1e 100%);
    min-height: 100vh;
}

/* ── Hide default Streamlit decoration ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

/* ── Main content padding ── */
.main .block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
}

/* ── Hero header ── */
.hero-header {
    text-align: center;
    padding: 3rem 2rem 2rem;
    position: relative;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    font-weight: 400;
    margin-bottom: 0.5rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a78bfa;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* ── Divider ── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #6366f1, #8b5cf6, transparent);
    margin: 1.5rem 0;
    border: none;
}

/* ── Cards ── */
.glass-card {
    background: rgba(15,23,42,0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(99,102,241,0.35);
}

/* ── Section labels ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.6rem;
}

/* ── Text areas ── */
.stTextArea textarea {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
    padding: 1rem !important;
    transition: border-color 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
.stTextArea textarea::placeholder { color: #475569 !important; }

/* ── Selectbox / dropdowns ── */
.stSelectbox > div > div {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Primary buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Download buttons ── */
.stDownloadButton > button {
    background: rgba(15,23,42,0.8) !important;
    color: #a78bfa !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100%;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: #6366f1 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px;
    padding: 0.8rem 1rem;
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: rgba(15,23,42,0.6) !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: rgba(15,23,42,0.4) !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Status colours ── */
.verdict-high  { color: #22c55e; font-weight: 700; }
.verdict-mid   { color: #f97316; font-weight: 700; }
.verdict-low   { color: #ef4444; font-weight: 700; }

/* ── Output text display ── */
.output-text-box {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.8;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 380px;
    overflow-y: auto;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}
.stat-item {
    font-size: 0.78rem;
    color: #64748b;
}
.stat-item span {
    color: #a78bfa;
    font-weight: 600;
}

/* ── Change summary ── */
.change-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    font-size: 0.88rem;
    color: #cbd5e1;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.change-item:last-child { border-bottom: none; }

/* ── Confidence bar ── */
.conf-bar-wrapper {
    background: rgba(15,23,42,0.6);
    border-radius: 50px;
    height: 8px;
    margin: 8px 0 4px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 50px;
    transition: width 0.8s ease;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,23,42,0.6);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(99,102,241,0.15);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(15,23,42,0.4); }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.7); }

/* ── Slider thumb ── */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: #6366f1 !important;
    border-color: #8b5cf6 !important;
}

/* ── Labels ── */
label[data-testid="stWidgetLabel"] p {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
</style>
""",
    unsafe_allow_html=True,
)


# ===========================================================================
# Session state initialisation
# ===========================================================================
def _init_state() -> None:
    """Initialise all required session state keys."""
    defaults = {
        "rewritten_text": "",
        "back_translation_text": "",
        "evaluation_result": None,
        "all_tones_results": [],
        "diff_html": "",
        "last_original": "",
        "last_tone": "",
        "last_audience": "",
        "last_length_pct": 100,
        "last_formality": 50,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ===========================================================================
# Sidebar — configuration
# ===========================================================================
def render_sidebar() -> tuple[str, str, int, int]:
    """
    Render the left sidebar controls and return user-selected parameters.

    Returns:
        Tuple of (tone, audience, length_pct, formality).
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 1rem 0 0.5rem;">
                <div style="font-size:2.5rem; margin-bottom:0.3rem;">🎯</div>
                <div style="font-size:1.1rem; font-weight:700; color:#a78bfa;">ToneShift</div>
                <div style="font-size:0.72rem; color:#475569; margin-top:2px;">Powered by Grok API</div>
            </div>
            <hr style="border:none; border-top:1px solid rgba(99,102,241,0.2); margin:1rem 0;">
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-label">🎨 Tone</div>', unsafe_allow_html=True)
        tone = st.selectbox(
            "Tone",
            options=[
                "Formal",
                "Casual",
                "Professional",
                "Friendly",
                "Child-Friendly",
                "Executive Summary",
                "Academic",
                "Marketing",
            ],
            label_visibility="collapsed",
        )

        st.markdown('<div class="section-label" style="margin-top:1rem;">👥 Audience</div>', unsafe_allow_html=True)
        audience = st.selectbox(
            "Audience",
            options=[
                "General Public",
                "Students",
                "Children",
                "Customers",
                "Developers",
                "Managers",
                "Executives",
                "HR",
            ],
            label_visibility="collapsed",
        )

        st.markdown('<div class="section-label" style="margin-top:1rem;">📏 Length</div>', unsafe_allow_html=True)
        length_pct = st.slider(
            "Length (%)",
            min_value=20,
            max_value=150,
            value=100,
            step=5,
            help="Target length as a percentage of the original text length.",
            label_visibility="collapsed",
        )
        st.markdown(
            f'<div style="font-size:0.75rem;color:#6366f1;text-align:center;margin-top:-0.5rem;">{length_pct}% of original</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-label" style="margin-top:1rem;">🎚️ Formality</div>', unsafe_allow_html=True)
        formality = st.slider(
            "Formality (0=casual, 100=very formal)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            label_visibility="collapsed",
        )
        formality_desc = (
            "Very Casual" if formality <= 20
            else "Casual" if formality <= 40
            else "Balanced" if formality <= 60
            else "Formal" if formality <= 80
            else "Very Formal"
        )
        st.markdown(
            f'<div style="font-size:0.75rem;color:#6366f1;text-align:center;margin-top:-0.5rem;">{formality}/100 · {formality_desc}</div>',
            unsafe_allow_html=True,
        )

        # ── API Key status ──
        st.markdown(
            '<hr style="border:none; border-top:1px solid rgba(99,102,241,0.2); margin:1.2rem 0;">',
            unsafe_allow_html=True,
        )
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            st.markdown(
                '<div style="text-align:center;font-size:0.78rem;color:#22c55e;">🟢 Groq API Connected</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align:center;font-size:0.78rem;color:#ef4444;">🔴 API Key Missing</div>',
                unsafe_allow_html=True,
            )
            st.caption("Set GROQ_API_KEY in your .env file.")

    return tone, audience, length_pct, formality


# ===========================================================================
# Hero Header
# ===========================================================================
def render_header() -> None:
    """Render the top hero header section."""
    st.markdown(
        """
        <div class="hero-header">
            <div class="hero-badge">✦ AI-Powered Writing Tool</div>
            <div class="hero-title">ToneShift</div>
            <div class="hero-subtitle">
                Rewrite text for different audiences while preserving meaning.
            </div>
        </div>
        <div class="gradient-divider"></div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
# Input section
# ===========================================================================
def render_input_section() -> str:
    """
    Render the text input area and return the user's input text.

    Returns:
        Raw input string.
    """
    st.markdown('<div class="section-label">✏️ Input Text</div>', unsafe_allow_html=True)
    input_text: str = st.text_area(
        label="Input Text",
        placeholder="Paste or type your text here...",
        height=220,
        key="input_text",
        label_visibility="collapsed",
    )

    if input_text.strip():
        wc = word_count(input_text)
        cc = char_count(input_text)
        rt = format_reading_time(input_text)
        st.markdown(
            f"""
            <div class="stats-bar">
                <div class="stat-item">Words: <span>{wc}</span></div>
                <div class="stat-item">Characters: <span>{cc}</span></div>
                <div class="stat-item">Reading: <span>{rt}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return input_text


# ===========================================================================
# Action buttons
# ===========================================================================
def render_action_buttons(input_text: str, tone: str, audience: str, length_pct: int, formality: int) -> None:
    """Render the primary action buttons and handle their click logic."""
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        rewrite_clicked = st.button("⚡ Rewrite", key="btn_rewrite")
    with col2:
        all_tones_clicked = st.button("🎭 Generate All Tones", key="btn_all_tones")
    with col3:
        clear_clicked = st.button("🗑 Clear", key="btn_clear")

    if clear_clicked:
        for key in [
            "rewritten_text", "back_translation_text", "evaluation_result",
            "all_tones_results", "diff_html",
        ]:
            st.session_state[key] = "" if isinstance(st.session_state[key], str) else ([] if isinstance(st.session_state[key], list) else None)
        st.rerun()

    if rewrite_clicked:
        _handle_rewrite(input_text, tone, audience, length_pct, formality)

    if all_tones_clicked:
        _handle_all_tones(input_text, audience, length_pct, formality)


def _handle_rewrite(
    input_text: str, tone: str, audience: str, length_pct: int, formality: int
) -> None:
    """Execute the full rewrite + back-translation + evaluation pipeline."""
    if not input_text.strip():
        st.error("⚠️ Please enter some text before rewriting.")
        return

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("🔑 GROQ_API_KEY is not set. Please add it to your .env file.")
        return

    try:
        # ── Step 1: Rewrite ──
        with st.spinner("✨ Rewriting with Grok..."):
            rewritten = rewrite_text(input_text, tone, audience, length_pct, formality)
            st.session_state["rewritten_text"] = rewritten
            st.session_state["last_original"] = input_text
            st.session_state["last_tone"] = tone
            st.session_state["last_audience"] = audience
            st.session_state["last_length_pct"] = length_pct
            st.session_state["last_formality"] = formality

        # ── Step 2: Diff ──
        with st.spinner("🔍 Generating diff view..."):
            st.session_state["diff_html"] = generate_html_diff(input_text, rewritten)

        # ── Step 3: Back-translation ──
        with st.spinner("🔄 Back-translating for meaning check..."):
            back_tr = back_translate(rewritten)
            st.session_state["back_translation_text"] = back_tr

        # ── Step 4: Evaluation ──
        with st.spinner("🧠 Evaluating meaning preservation..."):
            result = evaluate_meaning(input_text, back_tr)
            st.session_state["evaluation_result"] = result

    except EnvironmentError as exc:
        st.error(f"🔑 API Key Error: {exc}")
    except Exception as exc:
        st.error(f"❌ Something went wrong: {exc}")


def _handle_all_tones(
    input_text: str, audience: str, length_pct: int, formality: int
) -> None:
    """Generate all four preset tones in sequence."""
    if not input_text.strip():
        st.error("⚠️ Please enter some text first.")
        return

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("🔑 GROQ_API_KEY is not set. Please add it to your .env file.")
        return

    with st.spinner("🎭 Generating all four tones — this may take a moment..."):
        results = generate_all_tones(input_text, audience, length_pct, formality)
        st.session_state["all_tones_results"] = results


# ===========================================================================
# Output section
# ===========================================================================
def render_output_section() -> None:
    """Render side-by-side original / rewritten output with stats and actions."""
    rewritten = st.session_state.get("rewritten_text", "")
    original = st.session_state.get("last_original", "")

    if not rewritten:
        return

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">📄 Output</div>',
        unsafe_allow_html=True,
    )

    col_orig, col_rew = st.columns(2)

    with col_orig:
        st.markdown('<div class="section-label">Original</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="output-text-box">{original}</div>',
            unsafe_allow_html=True,
        )
        wc_o = word_count(original)
        st.markdown(
            f'<div class="stats-bar"><div class="stat-item">Words: <span>{wc_o}</span></div></div>',
            unsafe_allow_html=True,
        )

    with col_rew:
        st.markdown('<div class="section-label">Rewritten</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="output-text-box">{rewritten}</div>',
            unsafe_allow_html=True,
        )
        wc_r = word_count(rewritten)
        delta_pct = round(((wc_r - word_count(original)) / max(word_count(original), 1)) * 100)
        delta_str = f"+{delta_pct}%" if delta_pct >= 0 else f"{delta_pct}%"
        st.markdown(
            f'<div class="stats-bar"><div class="stat-item">Words: <span>{wc_r}</span></div>'
            f'<div class="stat-item">Change: <span>{delta_str}</span></div></div>',
            unsafe_allow_html=True,
        )

    # ── Change summary ──
    st.markdown('<div class="section-label" style="margin-top:1.2rem;">✅ Summary of Changes</div>', unsafe_allow_html=True)
    summary_items = build_change_summary(
        original_tone=None,
        tone=st.session_state.get("last_tone", ""),
        audience=st.session_state.get("last_audience", ""),
        length_pct=st.session_state.get("last_length_pct", 100),
        formality=st.session_state.get("last_formality", 50),
    )
    summary_html = "".join(
        f'<div class="change-item">{item}</div>' for item in summary_items
    )
    st.markdown(
        f'<div class="glass-card">{summary_html}</div>',
        unsafe_allow_html=True,
    )

    # ── Action buttons ──
    st.markdown('<div class="section-label" style="margin-top:0.5rem;">💾 Export</div>', unsafe_allow_html=True)
    col_cp, col_txt, col_pdf = st.columns(3)

    with col_cp:
        st.button("📋 Copy to Clipboard", key="btn_copy", on_click=_copy_to_clipboard, args=(rewritten,))

    with col_txt:
        txt_bytes = export_txt(
            original_text=original,
            rewritten_text=rewritten,
            tone=st.session_state.get("last_tone", ""),
            audience=st.session_state.get("last_audience", ""),
        )
        st.download_button(
            label="⬇ Download TXT",
            data=txt_bytes,
            file_name="toneshift_output.txt",
            mime="text/plain",
        )

    with col_pdf:
        back_tr = st.session_state.get("back_translation_text", "")
        eval_res = st.session_state.get("evaluation_result")
        pdf_bytes = export_pdf(
            original_text=original,
            rewritten_text=rewritten,
            tone=st.session_state.get("last_tone", ""),
            audience=st.session_state.get("last_audience", ""),
            back_translation=back_tr or None,
            verdict=eval_res.get("verdict") if eval_res else None,
            confidence=eval_res.get("confidence") if eval_res else None,
        )
        st.download_button(
            label="⬇ Download PDF",
            data=pdf_bytes,
            file_name="toneshift_output.pdf",
            mime="application/pdf",
        )


def _copy_to_clipboard(text: str) -> None:
    """Inject a JS snippet to copy text to clipboard."""
    safe = text.replace("`", "\\`").replace("\\", "\\\\")
    st.markdown(
        f"""
        <script>
        navigator.clipboard.writeText(`{safe}`).then(function() {{
            console.log('Copied!');
        }});
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.toast("✅ Copied to clipboard!", icon="📋")


# ===========================================================================
# Comparison view
# ===========================================================================
def render_diff_view() -> None:
    """Render the HTML diff comparison view."""
    diff_html = st.session_state.get("diff_html", "")
    if not diff_html:
        return

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    with st.expander("🔍 Comparison View — Highlighted Differences", expanded=False):
        st.markdown(
            "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.8rem;'>"
            "Green = added · Red = removed · Yellow = changed</p>",
            unsafe_allow_html=True,
        )
        st.iframe(diff_html, height=500, scrolling=True)


# ===========================================================================
# Back-translation section
# ===========================================================================
def render_back_translation() -> None:
    """Render the back-translation result."""
    back_tr = st.session_state.get("back_translation_text", "")
    if not back_tr:
        return

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-label">🔄 Back Translation</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#64748b;font-size:0.82rem;margin-bottom:0.8rem;'>"
        "The rewritten text was re-expressed in plain neutral English to check for meaning drift.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="output-text-box" style="border-color:rgba(139,92,246,0.3)">{back_tr}</div>',
        unsafe_allow_html=True,
    )


# ===========================================================================
# Meaning verification card
# ===========================================================================
def render_evaluation() -> None:
    """Render the meaning-verification evaluation card."""
    result = st.session_state.get("evaluation_result")
    if not result:
        return

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">🧠 Meaning Verification</div>',
        unsafe_allow_html=True,
    )

    confidence: int = result.get("confidence", 0)
    preserved: bool = result.get("meaning_preserved", False)
    missing: list = result.get("missing_information", [])
    added: list = result.get("added_information", [])
    verdict: str = result.get("verdict", "")

    color = confidence_color(confidence)
    clabel = confidence_label(confidence)

    # Low-confidence warning
    if confidence < 70:
        st.warning("⚠️ **Possible Meaning Drift Detected.** Review the details below carefully.")

    col_a, col_b = st.columns([1, 2])

    with col_a:
        preserved_icon = "✅" if preserved else "❌"
        preserved_text = "Preserved" if preserved else "Not Preserved"
        st.markdown(
            f"""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:3rem;">{preserved_icon}</div>
                <div style="font-size:0.75rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Meaning</div>
                <div style="font-size:1.2rem;font-weight:700;color:{'#22c55e' if preserved else '#ef4444'};">{preserved_text}</div>
                <div style="margin-top:1rem;">
                    <div style="font-size:2rem;font-weight:800;color:{color};">{confidence}%</div>
                    <div style="font-size:0.72rem;color:#94a3b8;">Confidence</div>
                </div>
                <div class="conf-bar-wrapper" style="margin-top:0.8rem;">
                    <div class="conf-bar-fill" style="width:{confidence}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
                </div>
                <div style="font-size:0.72rem;color:{color};margin-top:4px;font-weight:600;">{clabel}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="font-size:0.7rem;color:#6366f1;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;margin-bottom:0.8rem;">Verdict</div>
                <div style="font-size:0.95rem;color:#e2e8f0;line-height:1.6;margin-bottom:1rem;">"{verdict}"</div>
            """,
            unsafe_allow_html=True,
        )

        if missing:
            missing_html = "".join(f"<li style='margin:3px 0;'>{m}</li>" for m in missing)
            st.markdown(
                f"""
                <div style="margin-top:0.8rem;">
                    <div style="font-size:0.72rem;color:#ef4444;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">⚠ Missing Information</div>
                    <ul style="margin-top:6px;padding-left:1.2rem;font-size:0.85rem;color:#fca5a5;">{missing_html}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.82rem;color:#22c55e;margin-top:0.5rem;">✓ No missing information detected.</div>',
                unsafe_allow_html=True,
            )

        if added:
            added_html = "".join(f"<li style='margin:3px 0;'>{a}</li>" for a in added)
            st.markdown(
                f"""
                <div style="margin-top:0.8rem;">
                    <div style="font-size:0.72rem;color:#f97316;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">➕ Added Information</div>
                    <ul style="margin-top:6px;padding-left:1.2rem;font-size:0.85rem;color:#fed7aa;">{added_html}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.82rem;color:#22c55e;margin-top:0.5rem;">✓ No extraneous information added.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# All Tones section
# ===========================================================================
def render_all_tones() -> None:
    """Render expandable cards for the Generate All Tones results."""
    results = st.session_state.get("all_tones_results", [])
    if not results:
        return

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">🎭 All Tones</div>',
        unsafe_allow_html=True,
    )

    for item in results:
        emoji = item.get("emoji", "🔤")
        tone_name = item.get("tone", "")
        text = item.get("text", "")

        with st.expander(f"{emoji}  {tone_name}", expanded=False):
            st.markdown(
                f'<div class="output-text-box">{text}</div>',
                unsafe_allow_html=True,
            )
            wc = word_count(text)
            st.markdown(
                f'<div class="stats-bar" style="margin-top:0.6rem;">'
                f'<div class="stat-item">Words: <span>{wc}</span></div>'
                f'<div class="stat-item">Reading time: <span>{format_reading_time(text)}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            dl_bytes = export_txt(
                original_text=st.session_state.get("last_original", ""),
                rewritten_text=text,
                tone=tone_name,
                audience=st.session_state.get("last_audience", ""),
            )
            st.download_button(
                label=f"⬇ Download {tone_name} as TXT",
                data=dl_bytes,
                file_name=f"toneshift_{tone_name.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"dl_{tone_name}",
            )


# ===========================================================================
# Main entry point
# ===========================================================================
def main() -> None:
    """Orchestrate the full ToneShift application layout."""
    tone, audience, length_pct, formality = render_sidebar()
    render_header()

    input_text = render_input_section()

    st.markdown("<br>", unsafe_allow_html=True)
    render_action_buttons(input_text, tone, audience, length_pct, formality)

    # Output pipeline
    render_output_section()
    render_diff_view()
    render_back_translation()
    render_evaluation()

    # All tones
    render_all_tones()

    # Footer
    st.markdown(
        """
        <div style="text-align:center;margin-top:4rem;padding:2rem 0 1rem;
             border-top:1px solid rgba(99,102,241,0.1);color:#334155;font-size:0.75rem;">
            Made with ⚡ by ToneShift &nbsp;·&nbsp; Powered by Groq API · llama-3.1-8b-instant
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
