# 🎯 ToneShift — Audience-Aware Rewriter

> **Rewrite text for different audiences while preserving meaning.**
> Powered by the [Grok API (xAI)](https://console.x.ai/) and built with Python & Streamlit.

---

## 📖 Project Overview

**ToneShift** is a production-grade AI writing assistant that intelligently rewrites any text to suit a specific audience, tone, and formality level — while ensuring the original meaning is never lost.

After rewriting, ToneShift automatically:
1. **Back-translates** the rewritten text into neutral English
2. **Compares** it with the original using Grok's semantic understanding
3. **Presents a confidence score** and detailed verdict on whether the meaning was preserved

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 **8 Tones** | Formal, Casual, Professional, Friendly, Child-Friendly, Executive Summary, Academic, Marketing |
| 👥 **8 Audiences** | General Public, Students, Children, Customers, Developers, Managers, Executives, HR |
| 📏 **Length Control** | Scale output from 20% to 150% of original length |
| 🎚️ **Formality Slider** | Fine-tune from very casual (0) to very formal (100) |
| 🎭 **Generate All Tones** | Produce 4 rewrites simultaneously (Formal, Casual, Child-Friendly, Executive) |
| 🔍 **Diff View** | Side-by-side highlighted diff using `difflib.HtmlDiff` |
| 🔄 **Back-Translation** | Re-express rewritten text in neutral English for comparison |
| 🧠 **Meaning Verification** | Confidence score, missing/added info, and final verdict |
| 📋 **Copy to Clipboard** | One-click copy of rewritten output |
| ⬇️ **Export TXT / PDF** | Download results as formatted text or PDF |

---

## 🛠️ Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/)
- **Language**: Python 3.11+
- **LLM**: [Grok API (xAI)](https://console.x.ai/) via OpenAI-compatible SDK
- **Diff Viewer**: Python `difflib.HtmlDiff`
- **PDF Generation**: `fpdf2`
- **Environment**: `python-dotenv`

---

## 📁 Folder Structure

```
ToneShift/
│
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── README.md                     # This file
│
├── services/
│   ├── grok_client.py            # Grok API wrapper (OpenAI-compatible)
│   ├── rewrite_service.py        # Core rewrite logic + multi-tone generator
│   ├── back_translation.py       # Back-translation pipeline
│   ├── evaluation_service.py     # Meaning verification + JSON parsing
│   └── diff_view.py              # HTML diff generator (difflib)
│
├── prompts/
│   ├── rewrite_prompt.py         # Dynamic rewrite prompt builder
│   ├── back_translation_prompt.py# Back-translation prompt
│   └── evaluation_prompt.py      # Evaluation / meaning comparison prompt
│
├── utils/
│   ├── export.py                 # TXT and PDF export utilities
│   └── helpers.py                # Word count, reading time, confidence colour, etc.
│
└── assets/                       # Static assets (icons, images)
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/toneshift.git
cd toneshift
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure the Grok API

### Step 1 — Get your API key
1. Go to [https://console.x.ai/](https://console.x.ai/)
2. Sign in and navigate to **API Keys**
3. Create a new key and copy it

### Step 2 — Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env`:

```env
XAI_API_KEY=xai-your-actual-key-here
```

> ⚠️ **Never commit your `.env` file to version control.**

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** in your browser.

---

## 🚀 How to Use

1. **Paste or type** your text in the input area
2. **Select** Tone, Audience, Length, and Formality in the left sidebar
3. Click **⚡ Rewrite** for a single rewrite
4. Click **🎭 Generate All Tones** for four simultaneous rewrites
5. Review the **Comparison View**, **Back Translation**, and **Meaning Verification** below
6. **Export** your result as TXT or PDF

---

## 📸 Screenshots

> _Screenshots coming soon_

---

## 🔮 Future Improvements

- [ ] **Streaming output** — display tokens as they arrive for faster perceived performance
- [ ] **Custom tone builder** — allow users to define their own tone with example sentences
- [ ] **History panel** — persist and browse previous rewrites within the session
- [ ] **Multi-language support** — rewrite into/from languages other than English
- [ ] **Team workspace** — shared history and saved templates
- [ ] **API rate limiting** — add request queuing and retry with backoff
- [ ] **Tone scoring** — quantitatively score how close the rewrite matches the target tone

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
Made with ⚡ by ToneShift &nbsp;·&nbsp; Powered by <a href="https://x.ai">xAI Grok</a>
</div>
