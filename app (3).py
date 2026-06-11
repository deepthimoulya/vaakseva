import streamlit as st
from sarvamai import SarvamAI
import base64
import tempfile
import os

st.set_page_config(
    page_title="VaakSeva — Indic Voice Q&A",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
.main-title { font-size: 2rem; font-weight: 600; margin-bottom: 0.25rem; }
.subtitle { color: #888; font-size: 1rem; margin-bottom: 2rem; }
.mode-box { border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; border: 1px solid #e0e0e0; }
.mode-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.mode-text { font-size: 1rem; line-height: 1.6; }
.gap-box { background: #fff8e1; border: 1px solid #ffe082; border-radius: 10px; padding: 1rem 1.25rem; margin: 1rem 0; }
.answer-box { background: #f0f7ff; border: 1px solid #90caf9; border-radius: 10px; padding: 1.25rem; margin-top: 1rem; }
.token-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 0.5rem; }
.tok-kn { background: #ede7f6; color: #4527a0; padding: 3px 10px; border-radius: 20px; font-size: 0.85rem; }
.tok-en { background: #e3f2fd; color: #0d47a1; padding: 3px 10px; border-radius: 20px; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────
st.markdown('<div class="main-title">🎙️ VaakSeva</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Voice Q&A for code-mixed Kannada & Indian languages — powered by Sarvam AI</div>', unsafe_allow_html=True)

# ── API Key ──────────────────────────────────────────────────
api_key = st.secrets.get("SARVAM_API_KEY", "") or os.environ.get("SARVAM_API_KEY", "")
if not api_key:
    api_key = st.text_input("Enter your Sarvam API key", type="password",
                             help="Get a free key at dashboard.sarvam.ai")
if not api_key:
    st.info("Enter your Sarvam API key above to get started.")
    st.stop()

client = SarvamAI(api_subscription_key=api_key)

# ── Language selector ────────────────────────────────────────
LANGUAGES = {
    "Kannada": "kn-IN", "Hindi": "hi-IN", "Tamil": "ta-IN",
    "Telugu": "te-IN", "Malayalam": "ml-IN", "Marathi": "mr-IN",
    "Bengali": "bn-IN", "Gujarati": "gu-IN", "Punjabi": "pa-IN", "Odia": "or-IN",
}
col1, col2 = st.columns([2, 1])
with col1:
    lang_name = st.selectbox("Language", list(LANGUAGES.keys()), index=0)
with col2:
    lang_code = LANGUAGES[lang_name]
    st.markdown(f"<br><code>{lang_code}</code>", unsafe_allow_html=True)

st.divider()

# ── Audio input ──────────────────────────────────────────────
st.subheader("Step 1 — Provide audio input")

input_mode = st.radio("Choose input method", ["Upload audio file", "Generate sample (no mic needed)"], horizontal=True)

audio_path = None

if input_mode == "Upload audio file":
    uploaded = st.file_uploader("Upload a .wav or .mp3 file", type=["wav", "mp3", "m4a", "ogg"])
    if uploaded:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(uploaded.read())
        tmp.close()
        audio_path = tmp.name
        st.audio(uploaded)
        st.success("Audio uploaded!")

else:
    sample_sentences = {
        "Kannada": "Nanu office ge hogbekittu, but bus late aagide. Meeting yavaga start aaguttade?",
        "Hindi": "Main office ja raha hoon, but traffic bahut zyada hai. Meeting kab start hogi?",
        "Tamil": "Naan office ku poganum, but bus late aagidu. Meeting eppo start aagum?",
        "Telugu": "Nenu office ki vellaali, but bus late ayindi. Meeting eppudu start avutundi?",
        "Malayalam": "Ente office il pokename, but bus late ayi. Meeting evide start aakum?",
    }
    default_text = sample_sentences.get(lang_name,
        "I need to go to the office but the bus is late. When does the meeting start?")

    st.info(f"**Sample sentence:** *\"{default_text}\"*")
    st.caption("This is a real code-mixed sentence a speaker would say — mixing the local language with English.")

    if st.button("🔊 Generate audio using Sarvam TTS", use_container_width=True):
        with st.spinner("Generating audio with Bulbul v2..."):
            try:
                tts_response = client.text_to_speech.convert(
                    text=default_text,
                    target_language_code=lang_code,
                    speaker="anushka"
                )
                audio_data = base64.b64decode(tts_response.audios[0])
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp.write(audio_data)
                tmp.close()
                audio_path = tmp.name
                st.session_state["audio_path"] = audio_path
                st.session_state["sample_text"] = default_text
                st.audio(audio_data, format="audio/wav")
                st.success("Audio generated! Now transcribe it below.")
            except Exception as e:
                st.error(f"TTS error: {e}")

    if "audio_path" in st.session_state:
        audio_path = st.session_state["audio_path"]

# ── Transcription ────────────────────────────────────────────
if audio_path:
    st.divider()
    st.subheader("Step 2 — Transcribe with Saaras v3")

    if st.button("🧠 Transcribe in all 3 modes", use_container_width=True, type="primary"):
        results = {}
        with st.spinner("Running Saaras v3 in transcribe / translate / codemix modes..."):
            for mode in ["transcribe", "translate", "codemix"]:
                try:
                    with open(audio_path, "rb") as f:
                        resp = client.speech_to_text.transcribe(
                            file=f,
                            model="saaras:v3",
                            mode=mode,
                            language_code=lang_code
                        )
                    results[mode] = resp.transcript
                except Exception as e:
                    results[mode] = f"Error: {e}"

        st.session_state["results"] = results

    if "results" in st.session_state:
        results = st.session_state["results"]

        MODE_CONFIG = {
            "transcribe": ("📝 Transcribe", "#f3e5f5", "#6a1b9a", "Normalised output in the original script"),
            "translate":  ("🌐 Translate",  "#e8f5e9", "#1b5e20", "Clean English — use this as your RAG retrieval key"),
            "codemix":    ("🔀 Codemix",    "#fff3e0", "#e65100", "Mixed-script output preserving original style"),
        }

        for mode, (label, bg, color, tip) in MODE_CONFIG.items():
            text = results.get(mode, "")
            st.markdown(f"""
            <div class="mode-box" style="background:{bg}20; border-color:{bg};">
              <div class="mode-label" style="color:{color};">{label}</div>
              <div class="mode-text">{text}</div>
              <div style="font-size:0.75rem;color:#888;margin-top:6px;">{tip}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Retrieval gap analysis ───────────────────────────
        st.divider()
        st.subheader("Step 3 — The code-mixed retrieval gap")

        codemix_text = results.get("codemix", "")
        translate_text = results.get("translate", "")

        kn_tokens = [w for w in codemix_text.split() if any('\u0C80' <= c <= '\u0CFF' for c in w)]
        en_tokens = [w for w in codemix_text.split() if w.isalpha() and all(ord(c) < 128 for c in w)]

        kn_html = "".join(f'<span class="tok-kn">{w}</span>' for w in kn_tokens) if kn_tokens else "<i>none detected</i>"
        en_html = "".join(f'<span class="tok-en">{w}</span>' for w in en_tokens) if en_tokens else "<i>none detected</i>"

        st.markdown(f"""
        <div class="gap-box">
          <strong>⚠️ Why code-mixed queries break RAG retrieval</strong><br><br>
          The codemix output <b>spans two scripts at once</b>. Standard embedding models
          are trained on single-language text — so this query lands in an ambiguous space
          that doesn't match cleanly against English <em>or</em> {lang_name} documents.<br><br>
          <div style="margin-top:0.5rem;">
            <span style="font-size:0.8rem;font-weight:600;color:#4527a0;">
              {lang_name} script tokens detected:
            </span>
            <div class="token-row">{kn_html}</div>
          </div>
          <div style="margin-top:0.75rem;">
            <span style="font-size:0.8rem;font-weight:600;color:#0d47a1;">
              Latin (English) tokens detected:
            </span>
            <div class="token-row">{en_html}</div>
          </div>
          <div style="margin-top:1rem;padding-top:0.75rem;border-top:1px solid #ffe082;">
            ✅ <strong>Solution:</strong> Use the <b>translate</b> output as your retrieval key —
            it collapses both scripts into well-represented English embeddings.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Q&A with sarvam-105b ─────────────────────────────
        st.divider()
        st.subheader("Step 4 — Answer with sarvam-105b")

        kb = st.text_area(
            "Knowledge base (paste any text your assistant should know about)",
            value="""Company Meeting Schedule:
- Daily standup: 10:00 AM IST
- Weekly team meeting: Monday 11:00 AM IST
- Bus shuttle timings: 9:00 AM, 9:30 AM, 10:00 AM from main gate
- If running late, notify manager on Slack #delays channel""",
            height=140
        )

        if st.button("💬 Get answer from sarvam-105b", use_container_width=True, type="primary"):
            with st.spinner("Thinking with sarvam-105b..."):
                try:
                    response = client.chat.completions(
                        model="sarvam-105b",
                        messages=[
                            {"role": "system", "content": f"You are a helpful assistant. Answer only from this context:\n\n{kb}"},
                            {"role": "user", "content": translate_text}
                        ]
                    )
                    answer = response.choices[0].message.content
                    st.markdown(f"""
                    <div class="answer-box">
                      <div style="font-size:0.75rem;font-weight:600;color:#1565c0;margin-bottom:0.5rem;">
                        🤖 sarvam-105b answer (query: translated English)
                      </div>
                      <div style="font-size:1rem;line-height:1.7;">{answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"Query used for retrieval: *\"{translate_text}\"*")
                except Exception as e:
                    st.error(f"LLM error: {e}")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;font-size:0.8rem;color:#aaa;padding:1rem 0;">
  Built with <a href="https://sarvam.ai" target="_blank">Sarvam AI</a> —
  Saaras v3 · Bulbul v2 · sarvam-105b<br>
  <a href="https://github.com" target="_blank">GitHub</a> ·
  <a href="https://docs.sarvam.ai" target="_blank">Sarvam Docs</a>
</div>
""", unsafe_allow_html=True)
