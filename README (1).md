# VaakSeva — Indic Voice + Document Assistant for Government Schemes

A voice-first and document-aware government scheme eligibility assistant for Indian users. Built on Sarvam AI's full stack — Saaras v3 (STT), Bulbul v2 (TTS), Sarvam Vision (OCR), and sarvam-105b (LLM).

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit)](https://vaakseva-bitj6zzlu3wpvlepjddhy4.streamlit.app)
[![Sarvam AI](https://img.shields.io/badge/Powered%20by-Sarvam%20AI-5B4CF5)](https://sarvam.ai)

---

## The problem this solves

Real Indian users don't speak in clean, formal text. A Kannada speaker asking about a government scheme says:

> *"ಪಿಎಂ ಆವಾಸ್ ಯೋಜನೆಗೆ apply ಮಾಡಬಹುದಾ? ನಾನು BPL card holder ಇದ್ದೇನೆ."*

This is **code-mixing** — the query spans Kannada script and English in the same sentence. Standard STT and embedding models fail on this silently. VaakSeva handles it natively using Sarvam's Indic-first models.

---

## Features

**Tab 1 — 🎙️ Voice Q&A**
- Generate or upload audio in 10 Indian languages
- Transcribe using Saaras v3 in 3 modes: `transcribe`, `translate`, `codemix`
- Visualise the code-mixed retrieval gap (which tokens are Indic vs English)
- Answer using sarvam-105b grounded in real government scheme knowledge base

**Tab 2 — 📄 Document OCR**
- Upload ration card, Aadhaar, income certificate (PDF or image)
- Sarvam Vision extracts text from Indian-language documents
- sarvam-105b determines which schemes you may be eligible for

**Schemes covered:** PM Awas Yojana · PM Kisan · Ayushman Bharat · PM Ujjwala · Sukanya Samriddhi · MUDRA Loan · National Scholarship Portal

---

## Why Sarvam — not just any STT

| Challenge | Other models | Sarvam |
|-----------|-------------|--------|
| Code-mixed Indic speech | Fails or low accuracy | Native support via `codemix` mode |
| Indian-language documents | Poor OCR accuracy | Sarvam Vision trained on 22 Indian scripts |
| Indic script understanding | Secondary support | Purpose-built for India |

**Key insight:** Use Saaras v3's `translate` mode output — not the raw transcript — as the retrieval query. This collapses dual-script ambiguity into clean English embeddings.

---

## Setup

```bash
git clone https://github.com/yourusername/vaakseva
cd vaakseva
pip install -r requirements.txt
export SARVAM_API_KEY=your_key_here
streamlit run app.py
```

Get a free API key at [dashboard.sarvam.ai](https://dashboard.sarvam.ai)

---

## Deploy on Streamlit Cloud (free)

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select repo → `app.py`
3. Add secret: `SARVAM_API_KEY = "your_key"`
4. Deploy

---

## APIs used

| API | Model | Purpose |
|-----|-------|---------|
| Text-to-Speech | Bulbul v2 | Generate code-mixed audio sample |
| Speech-to-Text | Saaras v3 | Transcribe / translate / codemix modes |
| Document Intelligence | Sarvam Vision | OCR on Indian-language documents |
| Chat | sarvam-105b | Scheme eligibility answers |

---

## Architecture

```
User speaks (code-mixed Indic)
        ↓
Bulbul v2 TTS (text → audio)
        ↓
Saaras v3 STT (3 modes)
  ├── transcribe → original script
  ├── codemix   → mixed-script (shows the gap)
  └── translate → clean English ← used as retrieval query
        ↓
sarvam-105b (grounded in scheme knowledge base)
        ↓
Eligibility answer in English

OR

User uploads document (PDF/image)
        ↓
Sarvam Vision OCR
        ↓
sarvam-105b (scheme eligibility from extracted text)
```

---

## Built by

[Deepthi Moulya V M](https://linkedin.com/in/yourprofile) — CS fresher from Hassan, Karnataka
(2 km from the Halmidi inscription — oldest Kannada script on earth, 450 AD)

*Read the [blog post](https://docs.google.com/document/d/1Rz3Q7itqQ9uIVQofTNwkV1iNVqMfgWOHx4umdXqa8XM/edit?usp=sharing) for the full story behind this project.*
*Check out the demo here [demo](https://vaakseva-bitj6zzlu3wpvlepjddhy4.streamlit.app/) *
