import streamlit as st
import speech_recognition as sr
import time
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ────────────────────────────────
# AI PROMPT FUNCTIONS
# ────────────────────────────────

def get_follow_up_questions(transcript):
    prompt = f"""
You are an AI interview assistant. Given the candidate's answer below, generate 3 insightful follow-up interview questions the interviewer should ask next. Please note, the input might also be the interviewer's question. If that is the case, ignore or do not respond. Rate the Candidate's answer too.

Candidate's response:
\"\"\"{transcript}\"\"\"

Response Rating:

Interviewer questions:
"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def get_final_report(transcript):
    prompt = f"""
You are an AI interview assistant. Given the candidate's answer below, generate a report summarizing the candidate's responses, suitability, and overall performance.

Candidate's response:
\"\"\"{transcript}\"\"\"

Candidate Rating:

Interviewer Summary:
"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

# ────────────────────────────────
# Streamlit App Setup
# ────────────────────────────────

st.set_page_config(page_title="HireScope AI", layout="centered")
st.title("🤖 HireScope AI — Interview Assistant")

# Initialize session state
for key in ['transcript_history', 'listening', 'interview_started', 'followup_responses']:
    if key not in st.session_state:
        st.session_state[key] = "" if key == 'transcript_history' else False if key != 'followup_responses' else []

# ────────────────────────────────
# Start/Stop Interview
# ────────────────────────────────

if st.button("🚀 Start / Stop Interview"):
    st.session_state.interview_started = not st.session_state.interview_started
    st.session_state.listening = False  # Reset mic on interview toggle
    if not st.session_state.interview_started:
        # Clear everything on stop, optional
        st.session_state.transcript_history = ""
        st.session_state.followup_responses = []

if st.session_state.interview_started:
    st.success("🟢 Interview Active – You may now use mic and export tools.")
else:
    st.warning("🔒 Please start the interview to enable controls.")

# ────────────────────────────────
# Speech Recognition Functions
# ────────────────────────────────

recognizer = sr.Recognizer()

def listen_and_transcribe():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        st.toast("🎧 Listening... Speak now")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "[Unrecognized Speech]"
        except sr.RequestError as e:
            return f"[API Error: {e}]"
        except Exception as e:
            return f"[Error: {str(e)}]"

# ────────────────────────────────
# Mic Toggle Button
# ────────────────────────────────

mic_disabled = not st.session_state.interview_started
mic_btn = st.button("🎙️ Click to Mute/Unmute Mic", disabled=mic_disabled)

if mic_btn:
    st.session_state.listening = not st.session_state.listening

# ────────────────────────────────
# Live Listening & AI Feedback (appended in transcript)
# ────────────────────────────────

if st.session_state.listening and st.session_state.interview_started:
    st.success("🎙️ Mic On – Speak now!")
    placeholder = st.empty()
    while st.session_state.listening:
        new_text = listen_and_transcribe()

        # Generate AI follow-up questions for this candidate's response
        with st.spinner("🤖 Generating follow-up questions..."):
            followups = get_follow_up_questions(new_text)

        # Append candidate answer + AI suggestions inside transcript
        st.session_state.transcript_history += (
            f"Candidate: {new_text}\n"
            f"AI Suggestions:\n{followups}\n\n"
        )
        st.session_state.followup_responses.append((new_text, followups))
        placeholder.success("📝 Transcribed & AI Suggestions added")

        time.sleep(0.5)

elif not mic_disabled:
    st.info("🎤 Mic is Off")

# ────────────────────────────────
# Transcript Display
# ────────────────────────────────

st.subheader("🧾 Transcript Console")
st.text_area("Full Transcript", value=st.session_state.transcript_history, height=300, disabled=True)

# ────────────────────────────────
# Bottom Action Buttons
# ────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.button(
        "🧹 Clear Transcript",
        on_click=lambda: (st.session_state.update(transcript_history="", followup_responses=[])),
        disabled=not st.session_state.interview_started
    )

with col2:
    st.download_button(
        "💾 Download Transcript",
        st.session_state.transcript_history,
        file_name="transcript.txt",
        disabled=not st.session_state.interview_started
    )

st.markdown("---")
st.subheader("📄 Interview Summary Report")

if st.button("📤 Export Report", disabled=not st.session_state.interview_started):
    with st.spinner("🧠 Generating report..."):
        report = get_final_report(st.session_state.transcript_history)
        st.text_area("📋 HireScope AI Report", report, height=400)
        st.download_button("⬇️ Download Report", report, file_name="hirescope_interview_report.txt")
