# 🤖 Mini RAG Assessment App 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://minirag-app-w73elydxsbqwdnwmdbs4pl.streamlit.app)

[![Resume](https://img.shields.io/badge/Resume-Download-blue?style=for-the-badge&logo=adobeacrobatreader)](https://drive.google.com/file/d/1rk3qzjPqrmVb3LdmcPBW7AMhFatcVsXR/view?usp=sharing.com)

# Track - B 

An end-to-end **Retrieval-Augmented Generation (RAG)** system designed to perform high-accuracy question answering over PDF documents. This project implements a production-grade two-stage retrieval pipeline using Google's Gemini 2.0 and Cohere's Reranking technology.

## 🚀 Live Demo
**Check it out here:** [Live Streamlit Link](https://minirag-app-w73elydxsbqwdnwmdbs4pl.streamlit.app)

---

## 🛠️ Tech Stack & Architecture

This application leverages a modern AI stack to ensure speed, accuracy, and scalability:

* **LLM**: [Google Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/) (Stable 2026 version)
* **Vector Database**: [Pinecone](https://www.pinecone.io/) (Serverless AWS)
* **Embeddings**: `text-embedding-004` (768-dimensional vectors)
* **Reranker**: [Cohere Rerank v3.0](https://cohere.com/rerank)
* **Orchestration**: LangChain & Streamlit

### How it Works:

1.  **Ingestion**: PDFs are parsed and split using a `RecursiveCharacterTextSplitter` (600-char chunks with 50-char overlap).
2.  **Indexing**: Chunks are converted into high-dimensional embeddings and stored in Pinecone.
3.  **Retrieval**: A semantic search retrieves the top 10 most relevant chunks.
4.  **Reranking**: Cohere’s Reranker evaluates those 10 chunks against the user's query, selecting the top 3 most semantically dense sources.
5.  **Generation**: Gemini 2.0 synthesizes a grounded answer using only the provided context, featuring inline citations.

---

## ✨ Key Features

* **Hallucination Prevention**: Prompted to admit "I don't know" if the context doesn't contain the answer.
* **Two-Stage Search**: Combines the speed of vector search with the precision of a transformer-based reranker.
* **Grounded Citations**: Automatically cites sources [1], [2] to verify information.
* **State Management**: Real-time feedback on document indexing and vector upserting.

---

⚙️ Setup & Installation

Follow these steps to get a local copy of the project up and running for development and testing.

1. Prerequisites
Ensure you have the following installed:

Python 3.9 or higher

A Google AI Studio API Key (for Gemini & Embeddings)

A Pinecone API Key (and a created Index with 768 dimensions)

A Cohere API Key (for Reranking)

2. Environment Setup
   
Clone the repository and move into the project directory:
git clone https://github.com/Piyush-K-IIT/Mini_RAG-App.git
cd Mini_RAG-App

Create and activate a virtual environment to keep dependencies isolated:

# For Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# For Windows:
python -m venv venv
.\venv\Scripts\activate

3. Install Dependencies
Install all required libraries using the requirements.txt file you generated:

pip install -r requirements.txt



4. Local Secrets Configuration
Streamlit uses a specific hidden folder to manage API keys locally. You must create this manually:

( a ) Create a folder named .streamlit in the root directory.
( b ) Create a file inside it named secrets.toml.
( c ) Paste the following template into secrets.toml and add your real keys:

# .streamlit/secrets.toml
PINECONE_API_KEY = "your-pinecone-key"
GOOGLE_API_KEY = "your-google-gemini-key"
COHERE_API_KEY = "your-cohere-key"

5. Running the Application
Launch the Streamlit server from your terminal:
streamlit run mini-rag-app/app.py

The app will automatically open in your default web browser at http://localhost:8501


Remarks : Future Plan

I will build "Multimodal" RAG
Standard RAG only "sees" text. A top-tier improvement is allowing the AI to understand the images, tables, and charts inside your PDFs.

Table Extraction: Use tools like Unstructured or Camelot to parse tables into Markdown so the LLM can "read" the data rows properly.

Visual RAG: Use a multimodal model (like Gemini 1.5 Pro or GPT-4o) to describe images in the PDF. Store those descriptions in your vector database so you can "search" for images using text.

## 📊 Quality Evaluation ( 5 Q/A pairs )

| # | Question | Expected Answer | Result |
| :--- | :--- | :--- | :--- |
| 1 | Where was Gandhi born? | Gandhi was born in Porbandar | ✅ Pass |
| 2 | Years in South Africa? | Gandhi lived in South Africa for 21 years | ✅ Pass |
| 3 | Meaning of 'Mahatma'? | The honorific 'Mahatma' comes from Sanskrit and means "great-souled" or "venerable" | ✅ Pass |
| 4 | Significance of Dandi March? | The Dandi March, also known as the Salt March or Civil Disobedience Movement, was undertaken by Gandhi and volunteers who marched from Ahmedabad to Dandi, Gujarat, with the declared intention of breaking the salt laws | ✅ Pass |
| 5 | Who is Rohit Sharma | I don't know. The provided context does not contain information about Rohit Sharma. | ✅ Pass |
