# 🦅 Fed Watcher AI: Hybrid RAG for Monetary Policy Analysis

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Stack](https://img.shields.io/badge/Hybrid-Llama3%20(Local)%20%7C%20OpenAI%20(Cloud)-purple)
![Deployment](https://img.shields.io/badge/Deployment-Streamlit%20Cloud-FF4B4B)

### 🔴 Live Demo
**Click here to use the Cloud Version:** [Fed Watcher Pro (Streamlit Cloud)](https://fed-watcher-ai.streamlit.app/)  
*(Powered by GPT-4o-mini & ChromaDB)*

---

### 📊 Project Overview
Fed Watcher is a **Hybrid GenAI dashboard** designed to assist quantitative analysts and macro researchers. It ingests Federal Reserve FOMC minutes and uses **Retrieval-Augmented Generation (RAG)** to perform sentiment analysis ("Hawkish" vs. "Dovish") and answer specific policy questions with citation-backed accuracy.

### 🏗️ Hybrid Architecture (The "Engineer's Choice")
This project implements a unique **Dual-Backend** strategy to balance privacy, cost, and accessibility:

| Feature | 🏠 **Local Mode** | ☁️ **Cloud Mode** |
| :--- | :--- | :--- |
| **Use Case** | R&D, Privacy-First Analysis | Public Demo, Mobile Access |
| **LLM Backend** | **Ollama (Llama 3.1 8B)** | **OpenAI (GPT-4o-mini)** |
| **Hardware** | Runs on AMD Radeon RX 6700 XT | Serverless (Streamlit Cloud) |
| **Cost** | $0.00 (Local Compute) | ~$0.0006 per chat |
| **Privacy** | 100% Offline / Air-gapped | SOC 2 Compliant API |

### 🚀 Key Features
* **Automated Scraper:** Custom Python script to fetch historical FOMC minutes (2020-Present) directly from the Federal Reserve archives.
* **Vector Search Engine:** Uses **ChromaDB** to store semantic embeddings of financial texts, allowing for context-aware retrieval.
* **Hawkish/Dovish Gauge:** A custom "Sentiment Speedometer" built with **Plotly** that visualizes the aggregate policy stance of any selected meeting.
* **Smart Context Retrieval:** Retrieves the top-3 most relevant document chunks before generating an answer to prevent hallucinations.

### 🛠️ Technical Stack
* **Frontend:** Streamlit
* **Vector Database:** ChromaDB (Persistent Storage)
* **Local Inference:** Ollama + Llama 3.1
* **Cloud Inference:** OpenAI API (GPT-4o-mini)
* **Visualization:** Plotly Graph Objects

---

### 💻 How to Run

#### Option A: Run Locally (Free & Private)
*Requires [Ollama](https://ollama.com) installed.*

1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/samf0rd/fed-watcher-ai.git](https://github.com/samf0rd/fed-watcher-ai.git)
    cd fed-watcher-ai
    ```
2.  **Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (Windows: venv\Scripts\activate)
    pip install -r requirements.txt
    ```
3.  **Run with Ollama:**
    ```bash
    streamlit run app_local_ollama.py
    ```

#### Option B: Run with OpenAI (Cloud Ready)
*Requires an OpenAI API Key.*

1.  **Set your Key:**
    Create a `.streamlit/secrets.toml` file (or set it in your environment variables):
    ```toml
    OPENAI_API_KEY = "sk-..."
    ```
2.  **Run the Cloud App:**
    ```bash
    streamlit run streamlit_app.py
    ```

---
*Project developed by Samuel Garcia.*