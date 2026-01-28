# 🦅 Fed Watcher AI: Local RAG for Monetary Policy Analysis

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Stack](https://img.shields.io/badge/Tech-Llama3%20%7C%20Streamlit%20%7C%20ChromaDB-green)
![Status](https://img.shields.io/badge/Status-Prototype%20Complete-success)

### 📊 Project Overview
Fed Watcher is a **locally-hosted GenAI dashboard** designed to assist quantitative analysts and macro researchers. It ingests Federal Reserve FOMC minutes and uses **Retrieval-Augmented Generation (RAG)** to perform sentiment analysis ("Hawkish" vs. "Dovish") and answer specific policy questions with citation-backed accuracy.

Unlike cloud-based solutions, this architecture ensures **100% data privacy** by running the LLM (Llama 3.1) entirely on local hardware (AMD Radeon RX 6700 XT).

### 📺 Demo
![Demo GIF](assets/demo.gif)
*(If the GIF doesn't load, please check the /assets folder)*

### 🚀 Key Features
* **Automated Scraper:** Custom Python script to fetch historical FOMC minutes (2020-Present) directly from the Federal Reserve archives.
* **Vector Search Engine:** Uses **ChromaDB** to store semantic embeddings of financial texts, allowing for context-aware retrieval.
* **Hawkish/Dovish Gauge:** A custom "Sentiment Speedometer" built with **Plotly** that visualizes the aggregate policy stance of any selected meeting.
* **Local LLM Inference:** Powered by **Ollama (Llama 3.1 8B)**, optimized for consumer GPU hardware.

### 🛠️ Technical Architecture
* **Frontend:** Streamlit
* **LLM Backend:** Ollama (Llama 3.1)
* **Embedding Model:** Nomic-Embed-Text
* **Vector Database:** ChromaDB (Persistent Storage)
* **Visualization:** Plotly Graph Objects

### 💻 How to Run Locally

**Prerequisites:**
1.  Install [Ollama](https://ollama.com).
2.  Pull the required models:
    ```bash
    ollama pull llama3.1
    ollama pull nomic-embed-text
    ```

**Installation:**
```bash
# 1. Clone the repo
git clone [https://github.com/samf0rd/fed-watcher-ai.git](https://github.com/samf0rd/fed-watcher-ai.git)
cd fed-watcher-ai

# 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # (On Windows: venv\Scripts\activate)

# 3. Install Dependencies
pip install -r requirements.txt