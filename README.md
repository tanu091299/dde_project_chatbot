# 📊 DDE Project Chatbot

An interactive **RAG-based chatbot and analytics dashboard** for exploring and analyzing **Consistent High-Growth Firms (HGFs)** in Romania.

This project enables users to query company data using natural language and perform comparative analysis across firms.

---

## 🚀 Features

### 🤖 RAG-based Chatbot
- Ask questions like:
  - "Which companies are in fintech?"
  - "Find competitors of a company"
- Uses Retrieval-Augmented Generation (RAG)
- Converts structured data into conversational insights

### 📈 Company Comparison Tool
- Compare multiple companies side-by-side
- Analyze business descriptions and categories
- Useful for benchmarking and competitor analysis

### 🧠 AI-Driven Insights
- Built on AI-generated company descriptions
- Enables topic-based exploration and classification

---

## 🗂️ Project Structure, Installation, Usage, Dataset, and Tech Stack


dde_project_chatbot/
│
├── dde_rag_app.py        # RAG-based chatbot for Q&A
├── dde_comp_app.py       # Company comparison dashboard
├── romania_hgfs.xlsx     # Dataset of Romanian HGFs
├── requirements.txt      # Dependencies
└── README.md             # Documentation

This project is organized into two main application files: dde_rag_app.py for the chatbot and dde_comp_app.py for company comparison and analytics. The dataset is stored in romania_hgfs.xlsx, and all required Python libraries are listed in requirements.txt.

Installation

Clone the repository and install dependencies:

git clone https://github.com/tanu091299/dde_project_chatbot.git
cd dde_project_chatbot
pip install -r requirements.txt
Usage

Run the chatbot application:

python dde_rag_app.py

Run the company comparison dashboard:

python dde_comp_app.py
Dataset

The project uses a dataset of Romanian Consistent High-Growth Firms (HGFs), which includes:

Company names
AI-generated business descriptions
Industry and activity details

This dataset supports both natural language querying through the chatbot and structured analysis through the comparison dashboard.

Tech Stack
Python
Pandas
Streamlit
LLM-based RAG pipeline
Excel dataset
💡 Use Cases
Market research
Competitor analysis
Startup ecosystem exploration
Investment insights
Interactive data exploration using natural language
🔮 Future Improvements
Add filtering by industry and region
Improve semantic search with better embeddings
Deploy as a web application
Integrate external company data APIs
