# 📊 Spreadsheet AI Assistant

**Spreadsheet AI Assistant** is an AI-powered Streamlit app that enables users to:

- 📄 Automatically summarize data from uploaded `.csv`, `.xlsx`, or `.pdf` files
- 💬 Chat with an assistant to ask specific questions about the data
- 📤 Download results as **CSV** or **PDF** reports

Ideal for analysts, researchers, and decision-makers who want quick insights without writing code.

---

## ✨ Key Features

| Feature              | Description                                       |
| -------------------- | ------------------------------------------------- |
| 📁 File Upload       | Upload `.csv`, `.xlsx`, or `.pdf` documents |
| 📄 Summary Generator | Automatically summarizes uploaded file contents   |
| 💬 Chat Interface    | Ask AI-powered questions about the uploaded data  |
| 📤 Download Options  | Export responses and summaries to CSV or PDF      |

---

## 📂 Supported File Types

| File Type | Summary            | Chat   | Export      |
| --------- | ------------------ | ------ | ----------- |
| `.csv`  | ✅ Yes             | ✅ Yes | ✅ CSV, PDF |
| `.xlsx` | ✅ Yes             | ✅ Yes | ✅ CSV, PDF |
| `.pdf`  | ✅ Yes (text only) | ✅ Yes | ✅ PDF      |

---

## 🧠 What You Can Do

- **Summary Section** (auto-generated):

  > "This spreadsheet contains 3 sheets. Sales data is provided by region. The total revenue is $150K with a 20% increase in Q2."
  >
- **Chat Section** (interactive):

  > "Which product had the highest sales?"
  > "Summarize customer feedback trends."
  > "What are the major risks mentioned in the PDF?"
  >

---

## 🛠️ Installation

```bash
git clone https://github.com/ManideepMuddagowni/Spreadsheet-AI-Assistant.git
cd Spreadsheet-AI-Assistant
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 📤 Export Capabilities

| Output Type   | Description                                         |
| ------------- | --------------------------------------------------- |
| **CSV** | Saves chat/summary results in spreadsheet form      |
| **PDF** | Well-formatted PDF report with your Q&A and summary |

---

## 📦 Requirements

Install everything via:

```bash
pip install -r requirements.txt
```

Includes:

- `pandas`, `streamlit`
- `openai` (or equivalent LLM SDK ) - I Used GROQ
- `fpdf` for PDF
- `pdfplumber` / `PyMuPDF` for PDF text extraction

---

## 🔐 API Key Setup

Use a `.env` file in the root:

```env
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY = groq-api-key

```

---


## ✅ To Do (Optional Enhancements)

- [ ] File size limit indicator
- [ ] Multi-language support
