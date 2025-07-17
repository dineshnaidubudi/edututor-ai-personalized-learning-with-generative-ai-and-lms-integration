import streamlit as st
import random
import requests
import os
from questions import ai_questions, ml_questions, genai_questions, math_questions

# Hugging Face API Token (make sure this is valid)
HF_API_TOKEN = os.getenv("HF_TOKEN") or "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"
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-xl"

# Session state to keep question-answer history
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

def ask_huggingface_question(question):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"Answer this clearly: {question}"
    }
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        else:
            return "⚠️ Unexpected response format."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Request error: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error: {e}"

def get_question_set(subject):
    if subject == "Artificial Intelligence":
        return ai_questions
    elif subject == "Machine Learning":
        return ml_questions
    elif subject == "Generative AI":
        return genai_questions
    elif subject == "Mathematics":
        return math_questions
    return []

# UI Setup
st.set_page_config(page_title="EduTutor AI", layout="centered")
st.title("🎓 EduTutor AI")
st.markdown("Welcome to the AI-powered personalized learning assistant!")

panel = st.sidebar.selectbox("Select Panel", ["Student Panel", "Educator Panel"])

if panel == "Student Panel":
    tab1, tab2, tab3 = st.tabs(["📚 Take Quiz", "📊 Quiz History", "❓ Ask a Question"])

    with tab1:
        subject = st.selectbox("Choose Subject", ["Artificial Intelligence", "Machine Learning", "Generative AI", "Mathematics"])
        questions = get_question_set(subject)
        random.shuffle(questions)
        score = 0

        with st.form("quiz_form"):
            user_answers = {}
            for i, q in enumerate(questions[:10]):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                user_answers[q['question']] = st.radio("", q['options'], key=f"q_{i}")
            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            for q in questions[:10]:
                if user_answers[q['question']] == q['answer']:
                    score += 1
            st.success(f"✅ You scored {score}/10")

    with tab2:
        st.info("Quiz history will be available after backend integration.")

    with tab3:
        st.markdown("### 🤖 Ask a Question (powered by Hugging Face)")
        user_question = st.text_input("Ask your question:")
        if st.button("Get Answer"):
            with st.spinner("Getting answer..."):
                answer = ask_huggingface_question(user_question)
                st.success("Answer:")
                st.write(answer)
                st.session_state.qa_history.append({"question": user_question, "answer": answer})

        if st.session_state.qa_history:
            st.markdown("### 🧾 Your Question & Answer Dashboard")
            for i, entry in enumerate(reversed(st.session_state.qa_history)):
                st.markdown(f"**Q{i+1}:** {entry['question']}")
                st.markdown(f"🧠 **A:** {entry['answer']}")
                st.markdown("---")

elif panel == "Educator Panel":
    st.header("📊 Educator Dashboard")
    st.markdown("Monitor student engagement and quiz performance.")
    st.info("More analytics features coming soon!")
