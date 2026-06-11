# VaakSeva — Indic Voice Q&A powered by Sarvam AI

A voice-first Q&A web app for code-mixed Indian language inputs. Built on Sarvam's Saaras v3 (STT), Bulbul v2 (TTS), and sarvam-105b (LLM).

[![Open App](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit)](https://your-app.streamlit.app)

## The problem this solves

Real Indian users don't speak in clean, formal text. A query like *"Nanu hogbekitta but bus late aagide"* mixes Kannada script and English in the same sentence. Standard embedding models can't handle this — the query spans two scripts and breaks RAG retrieval silently.

**VaakSeva** demonstrates:
1. How Saaras v3 transcribes code-mixed speech in 3 modes (`transcribe` / `translate` / `codemix`)
2. Why `codemix` output breaks retrieval (visualised with token analysis)
3. Why `translate` mode is the correct retrieval key for Indic voice RAG
4. How sarvam-105b answers the question grounded in a knowledge base

## Setup

```bash
git clone https://github.com/yourusername/vaakseva
cd vaakseva
pip install -r requirements.txt
export SARVAM_API_KEY=your_key_here
streamlit run app.py
```

Get a free API key at [dashboard.sarvam.ai](https://dashboard.sarvam.ai)

## APIs used

| API | Model | Purpose |
|-----|-------|---------|
| Text-to-Speech | Bulbul v2 | Generate code-mixed audio sample |
| Speech-to-Text | Saaras v3 | Transcribe in transcribe / translate / codemix modes |
| Chat | sarvam-105b | Answer questions grounded in knowledge base |

## Deploy on Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select this repo → `app.py`
4. Add `SARVAM_API_KEY` in App secrets
5. Deploy

## Built by

[Deepthi Moulya V M](https://linkedin.com) — CS fresher from Hassan, Karnataka
