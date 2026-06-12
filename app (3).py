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
=== PM AWAS YOJANA GRAMIN (PMAY-G) — Rural Housing ===
- Who it's for: Homeless or kutcha house families in rural areas
- Eligibility: BPL families, SC/ST, minorities, persons with disabilities, manual scavengers, annual income below Rs 3 lakhs
- Not eligible: Families owning pucca house, government employees, income tax payers, families with motorised vehicles
- Benefit: Rs 1.20 lakh (plains), Rs 1.30 lakh (hilly/difficult areas), additional Rs 12,000 for toilet under SBM
- How to apply: Contact Gram Panchayat or apply via AwaasSoft portal (awaassoft.nic.in)
- Documents: Aadhaar card, bank account passbook, BPL certificate, job card (MGNREGA), photo

=== PM AWAS YOJANA URBAN (PMAY-U) — Urban Housing ===
- Who it's for: Urban poor, slum dwellers, EWS/LIG families
- Eligibility: EWS (income up to Rs 3 lakh), LIG (Rs 3-6 lakh), MIG-I (Rs 6-12 lakh), MIG-II (Rs 12-18 lakh)
- Benefit: Interest subsidy on home loans (3% to 6.5% depending on category), up to Rs 2.67 lakh subsidy
- How to apply: pmaymis.gov.in or nearest bank/housing finance company
- Documents: Aadhaar, income proof, bank account, property documents

=== PM KISAN SAMMAN NIDHI ===
- Who it's for: All landholding farmer families across India
- Eligibility: Farmer families with cultivable land. Not eligible: institutional landholders, government employees, income tax payers, doctors/lawyers/engineers
- Benefit: Rs 6,000 per year paid in 3 instalments of Rs 2,000 directly to bank account
- How to apply: pmkisan.gov.in or visit nearest CSC (Common Service Centre)
- Documents: Aadhaar card, land ownership records (Khasra/Khatauni), bank account, mobile number

=== AYUSHMAN BHARAT — PMJAY (Health Insurance) ===
- Who it's for: Poor and vulnerable families needing hospitalisation
- Eligibility: Families listed in SECC 2011 database, BPL families, construction workers, street vendors, domestic workers. Check at pmjay.gov.in
- Benefit: Rs 5 lakh health insurance per family per year, covers 1,500+ medical procedures, hospitalisation, surgery, ICU, medicines, pre and post hospitalisation
- How to apply: Check eligibility at pmjay.gov.in, visit any empanelled government or private hospital with Aadhaar
- Documents: Aadhaar card, ration card or family ID

=== PM UJJWALA YOJANA (Free LPG Connection) ===
- Who it's for: Women from poor households without LPG connection
- Eligibility: Women above 18 years from BPL households, SC/ST families, PM Awas Yojana beneficiaries, Antyodaya Anna Yojana families, forest dwellers, most backward classes
- Benefit: Free LPG connection (Rs 1,600 worth), first refill free, free stove (EMI option)
- How to apply: Visit nearest LPG distributor (HP, Bharat, Indane) with documents
- Documents: Aadhaar card, BPL certificate or ration card, bank account, address proof, passport photo

=== SUKANYA SAMRIDDHI YOJANA (Girl Child Savings) ===
- Who it's for: Parents or guardians of girl children
- Eligibility: Girl child below 10 years of age. Maximum 2 accounts per family (one per girl child)
- Benefit: 8.2% interest rate (highest among small savings schemes), tax exemption under Section 80C, maturity amount fully tax free
- Investment: Minimum Rs 250 per year, maximum Rs 1.5 lakh per year. Account matures after 21 years or at girl's marriage after age 18
- How to apply: Any post office or authorised bank (SBI, Bank of Baroda, Canara Bank etc.)
- Documents: Girl child's birth certificate, parent/guardian Aadhaar, address proof, photograph

=== PRADHAN MANTRI MUDRA YOJANA (Business Loans) ===
- Who it's for: Small business owners, shopkeepers, artisans, vendors, farmers doing allied activities
- Eligibility: Non-corporate, non-farm small/micro enterprises. No collateral required
- Loan types:
  * Shishu: Up to Rs 50,000 (new businesses, street vendors)
  * Kishor: Rs 50,001 to Rs 5 lakh (existing businesses needing expansion)
  * Tarun: Rs 5 lakh to Rs 10 lakh (well-established businesses)
- How to apply: Visit any bank, MFI (Microfinance Institution), NBFC, or mudra.org.in
- Documents: Aadhaar, PAN card, address proof, business proof, bank statement (6 months), 2 passport photos

=== NATIONAL SCHOLARSHIP PORTAL (NSP) ===
- Who it's for: Students from economically weaker sections across India
- Eligibility:
  * Pre-matric (Class 1-10): Minority students, SC/ST/OBC, income below Rs 1 lakh
  * Post-matric (Class 11 onwards): Minority students, SC/ST/OBC, income below Rs 2.5 lakhs
  * Merit-cum-means: Minority students in professional/technical courses, income below Rs 2.5 lakhs
- Benefit: Rs 1,000 to Rs 20,000 per year depending on scheme and level
- How to apply: scholarships.gov.in — register with Aadhaar, fill application before deadline (usually October-November)
- Documents: Income certificate, caste certificate, previous year marksheet, Aadhaar, bank account, institution verification

=== PM JAN DHAN YOJANA (Zero Balance Bank Account) ===
- Who it's for: Unbanked individuals across India
- Eligibility: Any Indian citizen above 10 years without a bank account
- Benefit: Zero balance savings account, RuPay debit card, Rs 1 lakh accident insurance, Rs 30,000 life cover, overdraft facility up to Rs 10,000 after 6 months
- How to apply: Visit any bank branch or BC (Business Correspondent) point
- Documents: Aadhaar card or any valid ID proof

=== ATAL PENSION YOJANA (Pension for Unorganised Workers) ===
- Who it's for: Unorganised sector workers without pension
- Eligibility: Indian citizens aged 18-40 years with a savings bank account. Not eligible: income tax payers
- Benefit: Guaranteed pension of Rs 1,000 to Rs 5,000 per month after age 60
- How to apply: Visit any bank or post office with savings account
- Documents: Aadhaar, savings bank account, mobile number

=== PM FASAL BIMA YOJANA (Crop Insurance) ===
- Who it's for: Farmers growing notified crops
- Eligibility: All farmers (loanee and non-loanee) growing notified crops in notified areas
- Benefit: Insurance coverage for crop loss due to natural calamities, pests, diseases. Sum insured equals scale of finance
- Premium: 2% for Kharif crops, 1.5% for Rabi crops, 5% for commercial/horticultural crops
- How to apply: Nearest bank, CSC centre, or pmfby.gov.in before crop season cutoff date
- Documents: Land records, Aadhaar, bank account, sowing certificate
"""

# ── Header ───────────────────────────────────────────────────
st.markdown("# VaakSeva")
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
    "🎙️ Voice Q&A  (Speech → LLM)",
    "📄 Document OCR  (Vision → LLM)"
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
        "Kannada":  "ಪಿಎಂ ಆವಾಸ್ ಯೋಜನೆಗೆ ಅರ್ಜಿ ಹಾಕಬೇಕು, ನಾನು BPL card ಹೊಂದಿದ್ದೇನೆ. Apply ಮಾಡುವುದು ಹೇಗೆ?",
        "Hindi":    "पीएम किसान योजना के लिए मैं eligible हूँ क्या? मेरे पास 2 एकड़ ज़मीन है।",
        "Tamil":    "ஆயுஷ்மான் பாரத் திட்டத்திற்கு நான் eligible ஆவேனா? என் குடும்பத்தில் 5 பேர் இருக்கிறோம்.",
        "Telugu":   "ముద్రా లోన్ కోసం apply చేయాలి, నేను small business start చేయాలనుకుంటున్నాను.",
        "Malayalam":"പിഎം ഉജ്ജ്വല യോജനക്ക് eligible ആണോ? ഞങ്ങൾ BPL family ആണ്.",
        "Marathi":  "सुकन्या समृद्धी योजनेत account उघडायचे आहे, मुलगी 5 वर्षांची आहे.",
        "Bengali":  "পিএম আবাস যোজনায় apply করতে চাই, আমার BPL card আছে।",
        "Gujarati": "મુદ્રા loan માટે apply કરવું છે, મારો business 2 lakh નો છે.",
        "Punjabi":  "ਪੀਐਮ ਕਿਸਾਨ scheme ਲਈ eligible ਹਾਂ, ਮੇਰੇ ਕੋਲ 3 acre ਜ਼ਮੀਨ ਹੈ।",
        "Odia":     "ଆୟୁଷ୍ମାନ ଭାରତ scheme ରେ eligible କି? ଆମ family BPL list ରେ ଅଛି।",
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

        # Allow user to type their own question
        custom_text = st.text_area(
            "Or type your own question (in your language)",
            placeholder=f"e.g. {default_text}",
            height=80,
            help="Type in your own language — Kannada, Hindi, Tamil, Telugu etc. Mix with English words freely."
        )
        # Use custom text if provided, else use sample
        tts_text = custom_text.strip() if custom_text.strip() else default_text

        if custom_text.strip():
            st.caption("Using your question: " + tts_text)

        if st.button("Generate audio with Bulbul v2", use_container_width=True):
            with st.spinner("Generating with Bulbul v2 TTS..."):
                try:
                    tts = client.text_to_speech.convert(
                        text=tts_text,
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
              <strong>⚠️ The code-mixed problem</strong><br><br>
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
            if st.button("Check eligibility", use_container_width=True, type="primary"):
                with st.spinner("sarvam-105b checking eligibility..."):
                    try:
                        SHORT_KB = """PM Awas Yojana: BPL families, SC/ST, income below 3 lakhs. Apply at Gram Panchayat.
PM Kisan: Farmers with land. Rs 6000/year. Apply at pmkisan.gov.in.
Ayushman Bharat: BPL families. Rs 5 lakh health cover. Apply at pmjay.gov.in.
PM Ujjwala: BPL women. Free LPG. Apply at LPG distributor.
Sukanya Samriddhi: Girl child below 10. 8.2% interest. Apply at post office.
MUDRA Loan: Small business. Up to Rs 10 lakh. Apply at any bank.
NSP Scholarship: SC/ST/OBC/Minority students, income below 2.5 lakh. Apply at scholarships.gov.in.
PM Jan Dhan: Any unbanked citizen. Zero balance account. Apply at any bank.
Atal Pension: Unorganised workers age 18-40. Rs 1000-5000 pension. Apply at bank."""
                        resp = client.chat.completions(
                            model="sarvam-105b",
                            messages=[
                                {"role":"system","content":f"You are a government scheme advisor. Answer the user's eligibility question using this scheme info:\n{SHORT_KB}\nGive a direct, helpful answer. Respond in {lang_name} language only."},
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
   

    DOC_LANG_NAMES = {
        "hi-IN":"Hindi","kn-IN":"Kannada","ta-IN":"Tamil","te-IN":"Telugu",
        "ml-IN":"Malayalam","mr-IN":"Marathi","bn-IN":"Bengali",
        "gu-IN":"Gujarati","pa-IN":"Punjabi","or-IN":"Odia","en-IN":"English"
    }
    doc_lang = st.selectbox("Document language", [
        "hi-IN","kn-IN","ta-IN","te-IN","ml-IN","mr-IN","bn-IN","gu-IN","pa-IN","or-IN","en-IN"
    ], index=1)
    doc_lang_name = DOC_LANG_NAMES.get(doc_lang, "Kannada")

    uploaded_doc = st.file_uploader(
        "Upload document (PDF, PNG, JPG)",
        type=["pdf","png","jpg","jpeg"],
        key="doc_upload"
    )

    if uploaded_doc:
        st.success(f"Uploaded: {uploaded_doc.name}")
        file_ext = uploaded_doc.name.split(".")[-1].lower() if "." in uploaded_doc.name else ""

        if uploaded_doc.type.startswith("image"):
            st.image(uploaded_doc, caption="Uploaded document", use_container_width=True)

        if st.button("🔍 Extract text with Sarvam Vision", use_container_width=True, type="primary"):
            with st.spinner("Extracting text from document..."):
                try:
                    extracted_text = ""

                    # Plain text files — read directly
                    if file_ext in ["txt"]:
                        extracted_text = uploaded_doc.read().decode("utf-8")
                        st.success("Text read from file!")

                    # PDF or Image — use Sarvam Vision API
                    else:
                        suffix = "." + file_ext
                        tmp_doc = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                        tmp_doc.write(uploaded_doc.read())
                        tmp_doc.close()

                        try:
                            job = client.document_intelligence.create_job(
                                language=doc_lang,
                                output_format="md"
                            )
                            job.upload_file(tmp_doc.name)
                            job.start()
                            job.wait_until_complete()

                            out_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
                            out_zip.close()
                            job.download_output(out_zip.name)

                            with zipfile.ZipFile(out_zip.name, "r") as z:
                                for name in z.namelist():
                                    if name.endswith(".md"):
                                        extracted_text = z.read(name).decode("utf-8")
                                        break
                                if not extracted_text:
                                    for name in z.namelist():
                                        if name.endswith(".json"):
                                            import json
                                            data = json.loads(z.read(name).decode("utf-8"))
                                            if isinstance(data, list):
                                                extracted_text = " ".join(
                                                    p.get("text","") for p in data
                                                )
                                            break
                            st.success("Text extracted with Sarvam Vision!")
                        except Exception as vision_error:
                            st.error(f"Vision OCR error: {vision_error}")

                    if extracted_text.strip():
                        st.session_state["ocr_text"] = extracted_text
                    else:
                        st.warning("No text could be extracted from this file.")

                except Exception as e:
                    st.error(f"Error reading file: {e}")

        if "ocr_text" in st.session_state:
            ocr_text = st.session_state["ocr_text"]
            st.markdown("**Extracted text:**")
            st.markdown(f'<div class="ocr-box">{ocr_text[:2000]}{"..." if len(ocr_text)>2000 else ""}</div>',
                       unsafe_allow_html=True)

            st.divider()
            st.markdown("**Now ask sarvam-105b — what schemes is this person eligible for?**")

            if st.button("Analyse document & check eligibility", use_container_width=True, type="primary"):
                with st.spinner("sarvam-105b analysing document..."):
                    try:
                        # Build prompt with ocr_text inline
                        current_ocr = st.session_state.get("ocr_text", "")
                        if not current_ocr.strip():
                            st.error("No text found. Please extract text first.")
                            st.stop()

                        SHORT_KB2 = """PM Awas Yojana: BPL families, SC/ST, income below 3 lakhs. Apply at Gram Panchayat.
PM Kisan: Farmers with land. Rs 6000/year. Apply at pmkisan.gov.in.
Ayushman Bharat: BPL families. Rs 5 lakh health cover. Apply at pmjay.gov.in.
PM Ujjwala: BPL women. Free LPG. Apply at LPG distributor.
Sukanya Samriddhi: Girl child below 10. 8.2% interest. Apply at post office.
MUDRA Loan: Small business. Up to Rs 10 lakh. Apply at any bank.
NSP Scholarship: SC/ST/OBC/Minority students, income below 2.5 lakh. Apply at scholarships.gov.in.
PM Jan Dhan: Any unbanked citizen. Zero balance account. Apply at any bank.
Atal Pension: Unorganised workers age 18-40. Rs 1000-5000 pension. Apply at bank."""
                        system_prompt = f"You are a government scheme advisor. Based on the document details, tell the person which schemes they are eligible for and how to apply. Use this reference:\n{SHORT_KB2}\nRespond in {doc_lang_name} language only."
                        user_prompt = f"My details from document:\n{current_ocr}\n\nWhich schemes am I eligible for?"

                        resp = client.chat.completions(
                            model="sarvam-105b",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ]
                        )
                        answer = resp.choices[0].message.content
                        if not answer or answer.strip().lower() == "none":
                            answer = "ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ." if doc_lang_name == "Kannada" else "Please try again."
                        st.markdown(f"""<div class="answer-box">
                          <div style="font-size:.75rem;font-weight:600;color:#276749;margin-bottom:.75rem;">
                            Scheme eligibility analysis
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
