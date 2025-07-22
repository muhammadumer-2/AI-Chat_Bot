# Tesla PDF Chatbot (Agentic Chat Interface)

This project is an **AI-powered chatbot** that reads and understands a PDF (`tesla.pdf`) and answers user questions based on its content. It includes built-in tools to:
- Record unanswered questions
- Capture user interest (via email)
- Notify using **Pushover**

The chatbot is built using:
- **OpenAI GPT-4o-mini**
- **Gradio** for UI
- **PDF parsing**
- Lightweight keyword-based document chunk retrieval (like mini-RAG)

---

## 🧠 Features

- ✅ Loads a Tesla-related PDF
- ✅ Splits it into chunks for efficient processing
- ✅ Extracts relevant chunks based on user question
- ✅ Prevents token limit overflow 
- ✅ Supports `record_user_details` and `record_unknown_question` tools
- ✅ Sends notifications via [Pushover](https://pushover.net/)

---

## 📁 Project Structure

├── app2.py # Main chatbot code
├── me/
│ └── tesla.pdf # Input PDF file
├── .env # Contains OpenAI and Pushover keys
└── README.md # This file


---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/tesla-pdf-chatbot.git
cd tesla-pdf-chatbot


# 2. Create a virtual environment and install dependencies

python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt


# Create a .env file in the root directory:

OPENAI_API_KEY=your_openai_api_key
PUSHOVER_TOKEN=your_pushover_app_token
PUSHOVER_USER=your_pushover_user_key

