import streamlit as st
from sarvamai import SarvamAI
import base64
import tempfile
import os
import zipfile
import time

st.set_page_config(
    page_title="VaakSeva — Government Scheme Assistant",
    page_icon="🏛️",
    layout="centered"
)

st.markdown("""
<style>
.mode-box{border-radius:10px;padding:1rem 1.25rem;margin-bottom:.75rem;border:1px solid #e0e0e0;}
.mode-label{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem;}
.mode-text{font-size:1rem;line-height:1.6;}
.gap-box{background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:1rem 1.25rem;margin:1rem 0;}
.answer-box{background:#f0fff4;border:1px solid #68d391;border-radius:10px;padding:1.25rem;margin-top:1rem;}
.token-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:.5rem;}
.tok-kn{background:#ede7f6;color:#4527a0;padding:3px 10px;border-radius:20px;font-size:.85rem;}
.tok-en{background:#e3f2fd;color:#0d47a1;padding:3px 10px;border-radius:20px;font-size:.85rem;}
.ocr-box{background:#f8f4ff;border:1px solid #c3aef5;border-radius:10px;padding:1rem 1.25rem;margin:1rem 0;font-size:.9rem;line-height:1.7;}
.badge{display:inline-block;font-size:.7rem;padding:2px 8px;border-radius:4px;font-weight:600;margin-left:6px;vertical-align:middle;}
.badge-new{background:#d1fae5;color:#065f46;}
</style>
""", unsafe_allow_html=True)

# ── Knowledge base ───────────────────────────────────────────
SCHEME_KB = """
PM Awas Yojana Gramin — Rural housing scheme:
- Eligibility: BPL families, SC/ST, minorities, persons with disabilities, annual income below 3 lakhs
- Benefit: Up to Rs 1.20 lakh plains, Rs 1.30 lakh hilly areas
- Apply: Gram Panchayat or AwaasSoft portal
- Documents: Aadhaar, bank account, BPL certificate

PM Kisan Samman Nidhi — Farmer income support:
- Eligibility: All landholding farmer families with cultivable land
- Benefit: Rs 6000 per year in 3 instalments of Rs 2000
- Apply: pmkisan.gov.in or nearest CSC centre
- Documents: Aadhaar, land records (Khasra/Khatauni), bank account

Ayushman Bharat PMJAY — Health insurance:
- Eligibility: Families in SECC database, BPL families
- Benefit: Rs 5 lakh health cover per family per year, covers hospitalisation, surgery, ICU, medicines
- Apply: pmjay.gov.in or nearest empanelled hospital
- Documents: Aadhaar, ration card

PM Ujjwala Yojana — Free LPG connection:
- Eligibility: Women from BPL households, SC/ST families, PMAY beneficiaries
- Benefit: Free LPG connection with first refill and stove
- Apply: Nearest LPG distributor
- Documents: Aadhaar, BPL/ration card, bank account

Sukanya Samriddhi Yojana — Girl child savings:
- Eligibility: Parents of girl child below 10 years
- Benefit: 8.2% interest rate, tax benefit under 80C
- Minimum: Rs 250/year, maximum Rs 1.5 lakh/year
- Apply: Post office or any bank
- Documents: Birth certificate, parent Aadhaar

National Scholarship Portal — Education scholarships:
- Eligibility: Minority/SC/ST/OBC students, income below 2.5 lakhs
- Benefit: Pre-matric and post-matric scholarships
- Apply: scholarships.gov.in
- Documents: Income certificate, caste certificate, marksheet, Aadhaar

Pradhan Mantri Mudra Yojana — Small business loans:
- Eligibility: Non-corporate small business, shopkeepers, artisans
- Loan types: Shishu up to 50000, Kishor 50000-5 lakh, Tarun 5-10 lakh
- Apply: Any bank, MFI, or mudra.org.in
- Documents: Business plan, Aadhaar, address proof, bank statement
"""

# ── Header ───────────────────────────────────────────────────
st.markdown("# 🏛️ VaakSeva")
st.markdown("**Voice + Document assistant for Indian government schemes** — powered by Sarvam AI")
st.caption("Ask about PM Awas, PM Kisan, Ayushman Bharat, Mudra Loan and more — in your own language")

# ── API Key ──────────────────────────────────────────────────
api_key = st.secrets.get("SARVAM_API_KEY", "") or os.environ.get("SARVAM_API_KEY", "")
if not api_key:
    api_key = st.text_input("Sarvam API key", type="password",
                             help="Free key at dashboard.sarvam.ai")
if not api_key:
    st.info("Enter your Sarvam API key to get started.")
    st.stop()

client = SarvamAI(api_subscription_key=api_key)

# ── Mode tabs ────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "Voice Q&A  (Speech → LLM)",
    "Document OCR  (Vision → LLM)"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — Voice Q&A
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Ask your question by voice")
    st.caption("Speak in any Indian language — even code-mixed — and get scheme eligibility answers")

    LANGUAGES = {
        "Kannada":"kn-IN","Hindi":"hi-IN","Tamil":"ta-IN","Telugu":"te-IN",
        "Malayalam":"ml-IN","Marathi":"mr-IN","Bengali":"bn-IN",
        "Gujarati":"gu-IN","Punjabi":"pa-IN","Odia":"or-IN",
    }
    SAMPLE_QUESTIONS = {
        "Kannada":  "PM Awas Yojana ge eligible aagalla, nanu BPL card holder idheeni. Apply maadodu hege?",
        "Hindi":    "PM Kisan yojana ke liye main eligible hoon kya? Mera 2 acre zameen hai.",
        "Tamil":    "Ayushman Bharat scheme ku eligible aaguvenu, en family kku 5 members irukku.",
        "Telugu":   "Mudra loan kosam apply cheyyali, nenu small business start cheyyali anukuntunna.",
        "Malayalam":"PM Ujjwala Yojana ku eligible aano? Njangal BPL family aanu.",
        "Marathi":  "Sukanya Samriddhi Yojana madhe account kadhaycha aahe, mulgi 5 varshachi aahe.",
        "Bengali":  "PM Awas Yojana te apply korte chai, aamar BPL card ache.",
        "Gujarati": "Mudra loan mate apply karvo chhe, maro business 2 lakh no chhe.",
        "Punjabi":  "PM Kisan scheme lyi eligible haan, mere kol 3 acre zameen hai.",
        "Odia":     "Ayushman Bharat scheme re eligible ki? Aamar family BPL list re ache.",
    }
    SCRIPT_RANGES = {
        "Kannada":('\u0C80','\u0CFF'),"Hindi":('\u0900','\u097F'),
        "Tamil":('\u0B80','\u0BFF'),"Telugu":('\u0C00','\u0C7F'),
        "Malayalam":('\u0D00','\u0D7F'),"Marathi":('\u0900','\u097F'),
        "Bengali":('\u0980','\u09FF'),"Gujarati":('\u0A80','\u0AFF'),
        "Punjabi":('\u0A00','\u0A7F'),"Odia":('\u0B00','\u0B7F'),
    }

    col1, col2 = st.columns([2,1])
    with col1:
        lang_name = st.selectbox("Language", list(LANGUAGES.keys()))
    with col2:
        lang_code = LANGUAGES[lang_name]
        st.markdown(f"<br><code>{lang_code}</code>", unsafe_allow_html=True)

    input_mode = st.radio("Input method",
        ["Generate sample (no mic needed)", "Upload audio file"], horizontal=True)

    audio_path = None

    if input_mode == "Upload audio file":
        uploaded = st.file_uploader("Upload .wav / .mp3 / .m4a", type=["wav","mp3","m4a","ogg"])
        if uploaded:
            suffix = "." + uploaded.name.split(".")[-1] if "." in uploaded.name else ".mp3"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(uploaded.read()); tmp.close()
            audio_path = tmp.name
            st.audio(uploaded)
            st.success("Uploaded!")
    else:
        default_text = SAMPLE_QUESTIONS.get(lang_name, SAMPLE_QUESTIONS["Hindi"])
        st.info(f"**Sample:** *\"{default_text}\"*")
        st.caption("Real code-mixed query — mixes local script with English terms like 'eligible', 'apply', 'BPL card'")

        if st.button("Generate audio with Bulbul v2", use_container_width=True):
            with st.spinner("Generating with Bulbul v2 TTS..."):
                try:
                    tts = client.text_to_speech.convert(
                        text=default_text,
                        target_language_code=lang_code,
                        speaker="anushka"
                    )
                    audio_data = base64.b64decode(tts.audios[0])
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tmp.write(audio_data); tmp.close()
                    audio_path = tmp.name
                    st.session_state["v_audio_path"] = audio_path
                    st.audio(audio_data, format="audio/mp3")
                    st.success("Done! Scroll down → Transcribe")
                except Exception as e:
                    st.error(f"TTS error: {e}")

        if "v_audio_path" in st.session_state:
            audio_path = st.session_state["v_audio_path"]

    if audio_path:
        st.divider()
        st.markdown("**Step 2 — Transcribe with Saaras v3**")

        if st.button("Transcribe in all 3 modes", use_container_width=True, type="primary"):
            results = {}
            with st.spinner("Running Saaras v3..."):
                for mode in ["transcribe","translate","codemix"]:
                    try:
                        ext = os.path.splitext(audio_path)[1].lstrip(".")
                        mime = f"audio/{ext}" if ext else "audio/mp3"
                        with open(audio_path,"rb") as f:
                            resp = client.speech_to_text.transcribe(
                                file=(os.path.basename(audio_path), f, mime),
                                model="saaras:v3", mode=mode, language_code=lang_code
                            )
                        results[mode] = resp.transcript
                    except Exception as e:
                        results[mode] = f"Error: {e}"
            st.session_state["v_results"] = results

        if "v_results" in st.session_state:
            results = st.session_state["v_results"]
            for mode, (label, bg, color, tip) in {
                "transcribe":("📝 Transcribe","#f3e5f5","#6a1b9a","Normalised original script"),
                "translate": ("🌐 Translate", "#e8f5e9","#1b5e20","Clean English — used as retrieval query"),
                "codemix":   ("🔀 Codemix",   "#fff3e0","#e65100","Mixed-script preserving original style"),
            }.items():
                st.markdown(f"""<div class="mode-box" style="background:{bg}20;border-color:{bg};">
                  <div class="mode-label" style="color:{color};">{label}</div>
                  <div class="mode-text">{results.get(mode,'')}</div>
                  <div style="font-size:.75rem;color:#888;margin-top:6px;">{tip}</div>
                </div>""", unsafe_allow_html=True)

            translate_text = results.get("translate","")
            codemix_text   = results.get("codemix","")

            lo, hi = SCRIPT_RANGES.get(lang_name,('\u0C80','\u0CFF'))
            native_tokens = [w for w in codemix_text.split() if any(lo<=c<=hi for c in w)]
            en_tokens     = [w for w in codemix_text.split() if w.isalpha() and all(ord(c)<128 for c in w)]
            native_html = "".join(f'<span class="tok-kn">{w}</span>' for w in native_tokens) or "<i>none</i>"
            en_html     = "".join(f'<span class="tok-en">{w}</span>' for w in en_tokens) or "<i>none</i>"

            st.divider()
            st.markdown("**Step 3 — Why this needs Sarvam (not just any STT)**")
            st.markdown(f"""<div class="gap-box">
              <strong>The code-mixed problem</strong><br><br>
              Real users say <em>"PM Awas ke liye eligible hoon kya?"</em> — not clean Hindi or clean English.
              This spans two scripts. English-only models don't understand it. Generic Hindi models miss
              English terms like <em>eligible, apply, BPL card</em>.<br><br>
              <span style="font-size:.8rem;font-weight:600;color:#4527a0;">{lang_name} tokens:</span>
              <div class="token-row">{native_html}</div>
              <div style="margin-top:.75rem;">
              <span style="font-size:.8rem;font-weight:600;color:#0d47a1;">English terms mixed in:</span>
              <div class="token-row">{en_html}</div></div>
              <div style="margin-top:1rem;padding-top:.75rem;border-top:1px solid #ffe082;">
              ✅ <strong>Sarvam fix:</strong> Saaras v3 handles this natively.
              The <b>translate</b> output gives a clean English query for retrieval.
              </div></div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("**Step 4 — Get answer from sarvam-105b**")
            if st.button("🏛️ Check eligibility", use_container_width=True, type="primary"):
                with st.spinner("sarvam-105b checking eligibility..."):
                    try:
                        resp = client.chat.completions(
                            model="sarvam-105b",
                            messages=[
                                {"role":"system","content":f"You are a helpful Indian government scheme assistant. Answer eligibility questions based on:\n{SCHEME_KB}\nBe clear and specific. Mention documents needed."},
                                {"role":"user","content":translate_text}
                            ]
                        )
                        answer = resp.choices[0].message.content
                        st.markdown(f"""<div class="answer-box">
                          <div style="font-size:.75rem;font-weight:600;color:#276749;margin-bottom:.75rem;">🏛️ sarvam-105b answer</div>
                          <div style="font-size:1rem;line-height:1.8;">{answer}</div>
                        </div>""", unsafe_allow_html=True)
                        st.caption(f"Query used: *\"{translate_text}\"*")
                    except Exception as e:
                        st.error(f"LLM error: {e}")

# ════════════════════════════════════════════════════════════
# TAB 2 — Document OCR (Vision)
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Upload a document — Sarvam Vision reads it")
    st.markdown(
        "Upload a **ration card, Aadhaar, income certificate, or any government document** "
        "(PDF or image). Sarvam Vision extracts the text — then sarvam-105b tells you "
        "which schemes you may be eligible for."
    )
    st.info(
        "**Why Sarvam Vision?** Government documents in India are in regional scripts — "
        "Kannada, Hindi, Tamil, Telugu. Global OCR models fail on these. "
        "Sarvam Vision is trained on 22 Indian languages natively.",
        icon="ℹ️"
    )

    doc_lang = st.selectbox("Document language", [
        "hi-IN","kn-IN","ta-IN","te-IN","ml-IN","mr-IN","bn-IN","gu-IN","pa-IN","or-IN","en-IN"
    ], index=1)

    uploaded_doc = st.file_uploader(
        "Upload document (PDF, PNG, JPG)",
        type=["pdf","png","jpg","jpeg"],
        key="doc_upload"
    )

    if uploaded_doc:
        st.success(f"Uploaded: {uploaded_doc.name}")
        if uploaded_doc.type.startswith("image"):
            st.image(uploaded_doc, caption="Uploaded document", use_container_width=True)

        if st.button("🔍 Extract text with Sarvam Vision", use_container_width=True, type="primary"):
            with st.spinner("Running Sarvam Vision OCR — extracting text from document..."):
                try:
                    # Save uploaded file
                    suffix = "." + uploaded_doc.name.split(".")[-1]
                    tmp_doc = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tmp_doc.write(uploaded_doc.read())
                    tmp_doc.close()

                    # Create job
                    job = client.document_intelligence.create_job(
                        language=doc_lang,
                        output_format="md"
                    )
                    # Upload file
                    job.upload_file(tmp_doc.name)
                    # Start
                    job.start()
                    # Wait
                    status = job.wait_until_complete()

                    # Download output zip
                    out_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
                    out_zip.close()
                    job.download_output(out_zip.name)

                    # Extract markdown from zip
                    extracted_text = ""
                    with zipfile.ZipFile(out_zip.name, "r") as z:
                        for name in z.namelist():
                            if name.endswith(".md"):
                                extracted_text = z.read(name).decode("utf-8")
                                break
                        if not extracted_text:
                            # Try JSON
                            for name in z.namelist():
                                if name.endswith(".json"):
                                    import json
                                    data = json.loads(z.read(name).decode("utf-8"))
                                    if isinstance(data, list):
                                        extracted_text = " ".join(
                                            p.get("text","") for p in data
                                        )
                                    break

                    st.session_state["ocr_text"] = extracted_text
                    st.success("Text extracted!")

                except Exception as e:
                    st.error(f"Vision OCR error: {e}")

        if "ocr_text" in st.session_state:
            ocr_text = st.session_state["ocr_text"]
            st.markdown("**Extracted text:**")
            st.markdown(f'<div class="ocr-box">{ocr_text[:2000]}{"..." if len(ocr_text)>2000 else ""}</div>',
                       unsafe_allow_html=True)

            st.divider()
            st.markdown("**Now ask sarvam-105b — what schemes is this person eligible for?**")

            if st.button("🏛️ Analyse document & check eligibility", use_container_width=True, type="primary"):
                with st.spinner("sarvam-105b analysing document..."):
                    try:
                        resp = client.chat.completions(
                            model="sarvam-105b",
                            messages=[
                                {"role":"system","content":f"""You are a helpful Indian government scheme advisor.
Based on the document text provided, identify what information is available
(name, income, category, family details etc.) and tell the person:
1. Which government schemes they appear eligible for
2. What to do next to apply
3. What additional documents they may need

Use this scheme knowledge:
{SCHEME_KB}"""},
                                {"role":"user","content":f"Here is the extracted text from my document:\n\n{ocr_text}\n\nWhich government schemes am I eligible for?"}
                            ]
                        )
                        answer = resp.choices[0].message.content
                        st.markdown(f"""<div class="answer-box">
                          <div style="font-size:.75rem;font-weight:600;color:#276749;margin-bottom:.75rem;">
                            🏛️ Scheme eligibility analysis
                          </div>
                          <div style="font-size:1rem;line-height:1.8;">{answer}</div>
                        </div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"LLM error: {e}")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;font-size:.8rem;color:#aaa;padding:1rem 0;">
  Built with <a href="https://sarvam.ai" target="_blank">Sarvam AI</a><br>
  Saaras v3 (STT) · Bulbul v2 (TTS) · Sarvam Vision (OCR) · sarvam-105b (LLM)<br>
  Voice + Vision + LLM pipeline · 10 Indian languages<br>
  <a href="https://github.com" target="_blank">GitHub</a> ·
  <a href="https://docs.sarvam.ai" target="_blank">Docs</a>
</div>
""", unsafe_allow_html=True)
