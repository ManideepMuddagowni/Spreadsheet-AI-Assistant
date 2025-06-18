import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Check API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ Please set the GROQ_API_KEY environment variable.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# ------------------ UTILS ------------------ #

def get_pdf_text(pdf_files):
    text = ""
    for pdf_file in pdf_files:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def get_csv_text(csv_files):
    texts = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            texts.append(df.to_string(index=False))
        except Exception as e:
            texts.append(f"Error reading CSV: {e}")
    return "\n\n".join(texts)

def chunk_text(text, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

def create_prompt(chunks, conversation, question, max_context_tokens=3000):
    context = ""
    tokens = 0
    for chunk in chunks:
        if tokens + len(chunk) > max_context_tokens:
            break
        context += chunk + "\n"
        tokens += len(chunk)

    history_text = ""
    for turn in conversation:
        role = turn["role"]
        content = turn["content"]
        history_text += f"{role.capitalize()}: {content}\n"

    prompt = f"""
You are a helpful assistant. Use the following context to answer the question below. If the answer is not in the context, say "Answer is not available in the context."

Context:
{context}

Conversation History:
{history_text}

Current Question:
{question}

Answer:
"""
    return prompt

def query_groq(prompt):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content

# ------------------ UI ------------------ #

def main():
    st.set_page_config(page_title="AI PDF/CSV Assistant", page_icon="🧠", layout="wide")

    st.markdown(
        """
        <style>
        .big-title {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .chat-bubble-user {
            background-color: #3498db;
            color: white;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 8px;
        }
        .chat-bubble-assistant {
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="big-title">📊 AI Assistant for PDFs and Spreadsheets</div>', unsafe_allow_html=True)
    st.write("Chat with your data using LLaMA 3.1 (Groq API powered)")

    with st.sidebar:
        st.header("📁 File Type & Upload")
        file_type = st.selectbox("Select file type:", ["PDF", "CSV"])

        uploaded_files = None
        if file_type == "PDF":
            uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type=["pdf"])
        elif file_type == "CSV":
            uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])

        process_files = st.button("🚀 Process Files")

    if "chunks" not in st.session_state:
        st.session_state["chunks"] = []

    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []

    if uploaded_files and process_files:
        with st.spinner("🔍 Extracting and chunking text..."):
            combined_text = ""
            if file_type == "PDF":
                combined_text = get_pdf_text(uploaded_files)
            elif file_type == "CSV":
                combined_text = get_csv_text(uploaded_files)

            if combined_text.strip():
                chunks = chunk_text(combined_text)
                st.session_state["chunks"] = chunks
                st.session_state["conversation"] = []
                st.success(f"✅ Processed {file_type} into {len(chunks)} chunks.")

    st.markdown("---")
    st.subheader("💬 Ask Questions")

    chat_container = st.container()
    for msg in st.session_state["conversation"]:
        with chat_container:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">👤 <strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-assistant">🤖 <strong>Assistant:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""

    def submit():
        user_input = st.session_state.input_text
        if user_input:
            st.session_state.conversation.append({"role": "user", "content": user_input})

            if st.session_state["chunks"]:
                with st.spinner("🧠 Thinking..."):
                    prompt = create_prompt(st.session_state["chunks"], st.session_state["conversation"], user_input)
                    answer = query_groq(prompt)
            else:
                answer = "⚠️ Please upload and process a file first."

            st.session_state.conversation.append({"role": "assistant", "content": answer})
            st.session_state.input_text = ""

    st.text_input("Type your question here...", key="input_text", on_change=submit, placeholder="Ask me anything from the uploaded file")

if __name__ == "__main__":
    main()
