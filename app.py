import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import os
import tiktoken
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ Please set the GROQ_API_KEY environment variable.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")  

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
            meta_info = f"CSV has {df.shape[0]} rows and {df.shape[1]} columns.\nColumns: {', '.join(df.columns)}\n"
            sample = df.head(10).to_markdown(index=False)
            texts.append(meta_info + "\nSample Data:\n" + sample)
        except Exception as e:
            texts.append(f"Error reading CSV: {e}")
    return "\n\n".join(texts)

def chunk_text(text, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

def count_tokens(text):
    return len(enc.encode(text))

def create_prompt(chunks, conversation, question, max_context_tokens=3000):
    context = ""
    tokens = 0
    for chunk in chunks:
        chunk_tokens = count_tokens(chunk)
        if tokens + chunk_tokens > max_context_tokens:
            break
        context += chunk + "\n"
        tokens += chunk_tokens

    # Limit conversation history to last 4 turns
    history_text = ""
    for turn in conversation[-4:]:
        role = turn["role"]
        content = turn["content"]
        history_text += f"{role.capitalize()}: {content}\n"

    prompt = f"""
You are a helpful AI assistant that can analyze and summarize tabular or document data provided in the context.

Using only the data in the context, generate a clear, well-structured, and human-readable summary.

- If the data is tabular, summarize each row as a labeled list of key-value pairs.
- If the data contains multiple fields, display all fields clearly with labels.
- Use bullet points, line breaks, and short paragraphs for clarity.
- Use "Not available" if a value is missing.
- Do not invent any data outside the context.
- Avoid raw JSON or code formats; make the output readable.

Context:
{context}

Conversation History:
{history_text}

Question:
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

    st.markdown("""
        <style>
        .big-title {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
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
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="big-title">📊 AI Assistant for PDFs and Spreadsheets</div>', unsafe_allow_html=True)
    st.write("Chat with your data using Meta - LLaMA 3.1 (via Groq API)")

    with st.sidebar:
        st.header("📁 Upload Files")
        file_type = st.selectbox("Select file type:", ["PDF", "CSV"])
        uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True, type=["pdf", "csv"])
        process_files = st.button("🚀 Process Files")

    if "chunks" not in st.session_state:
        st.session_state["chunks"] = []

    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []

    if "summary" not in st.session_state:
        st.session_state["summary"] = ""

    left_col, right_col = st.columns([2, 1])

    with left_col:
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

                    # Generate summary
                    summary_prompt = f"""
You are a summarizer. Read the content and produce a clear, structured summary.
- For CSV: Explain structure, headers, rows, sample data.
- For PDF: Structure into sections like Intro, Methods, etc.

Content:
{combined_text[:3000]}

Summary:
"""
                    summary = query_groq(summary_prompt)
                    st.session_state["summary"] = summary
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
                        prompt = create_prompt(
                            st.session_state["chunks"],
                            st.session_state["conversation"],
                            user_input
                        )
                        answer = query_groq(prompt)
                else:
                    answer = "⚠️ Please upload and process a file first."

                st.session_state.conversation.append({"role": "assistant", "content": answer})
                st.session_state.input_text = ""

                if debug_mode:
                    st.markdown("### 🧪 Debug Prompt")
                    st.code(prompt)

        # Text input with on_change triggers submit() (Enter key)
        st.text_input(
            "Type your question here...", 
            key="input_text", 
            on_change=submit, 
            placeholder="Ask about your file data"
        )

        # Submit button to trigger submit manually
        if st.button("Send"):
            submit()

    with right_col:
        st.subheader("📝 Summary")
        if st.session_state["summary"]:
            st.markdown(st.session_state["summary"])
        else:
            st.info("Upload and process a file to generate a summary here.")

if __name__ == "__main__":
    main()
