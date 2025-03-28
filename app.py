import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
import openai
import PyPDF2
import os

# Set up Streamlit page
st.set_page_config(page_title="Notebook LM", page_icon="📖", layout="wide")

# Sidebar Navigation
st.sidebar.title("🔍 AI Notebook Menu")
page = st.sidebar.radio("Navigate", ["📖 Notebook", "📂 Summarization", "⚙️ Settings"])

# Sidebar - OpenAI API Key Input
st.sidebar.subheader("🔑 API Configuration")
openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# Sidebar - Model Selection
st.sidebar.subheader("🤖 Model Selection")
model_choice = st.sidebar.selectbox("Choose a model", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])

# Sidebar - Extra Info
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Notebook LM** is an AI-powered assistant for writing, summarizing, and note-taking.")

# Function to generate AI response
def generate_response(prompt):
    if not openai_api_key or not openai_api_key.startswith("sk-"):
        st.warning("⚠ Please enter a valid OpenAI API key!", icon="⚠")
        return None

    try:
        model = ChatOpenAI(temperature=0.7, api_key=openai_api_key, model_name=model_choice)
        response = model.invoke(prompt)
        return response.content.strip()

    except openai.RateLimitError:
        st.error("🚨 Rate Limit Exceeded: Check your OpenAI billing details and usage.")
        return None

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# 📖 Notebook Page
if page == "📖 Notebook":
    st.title("📖 AI Notebook - Take Notes & Generate Insights")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_area("✍️ Write your notes or questions:", height=200)

    if st.button("Generate Response ✨"):
        if user_input.strip():
            response = generate_response(user_input)
            if response:
                st.session_state.chat_history.append(("📝 You", user_input))
                st.session_state.chat_history.append(("🤖 AI", response))

    # Display chat history
    st.subheader("📜 Notebook Entries")
    for role, text in st.session_state.chat_history:
        if role == "📝 You":
            st.markdown(f"**{role}:** {text}")
        else:
            st.success(f"**{role}:** {text}")

# 📂 Summarization Page
elif page == "📂 Summarization":
    st.title("📂 Upload & Summarize Files")
    
    uploaded_file = st.file_uploader("📤 Upload a PDF or TXT file", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1]

        if file_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        else:  # Text file
            text = uploaded_file.getvalue().decode("utf-8")

        st.text_area("📜 Extracted Content", text, height=300)

        if st.button("Summarize ✨"):
            summary = generate_response(f"Summarize this text:\n{text[:2000]}")
            if summary:
                st.session_state["doc_summary"] = summary
                st.subheader("📌 AI-Generated Summary")
                st.success(summary)

        # Interactive Q&A on summary
        if "doc_summary" in st.session_state:
            st.subheader("🔍 Ask about the document")
            user_question = st.text_input("Ask a question (e.g., 'Give an example from the text')")
            
            if st.button("Get Answer"):
                follow_up = generate_response(f"Based on the document, {user_question}")
                if follow_up:
                    st.subheader("📖 AI Response")
                    st.info(follow_up)

# ⚙️ Settings Page
elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Preferences")
    st.write("Configure your AI Notebook settings here.")
    
    temperature = st.slider("Creativity Level (Temperature)", 0.0, 1.0, 0.7)
    st.write(f"🧠 Model Creativity: `{temperature}`")

    if st.button("Save Settings"):
        st.success("✅ Settings saved!")
