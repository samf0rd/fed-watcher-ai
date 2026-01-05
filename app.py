import streamlit as st
import ollama
import chromadb
import os
from pypdf import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fed Watcher AI",
    page_icon="🦅",
    layout="wide"
)

# --- BACKEND SETUP ---
# Initialize the database client
# We use the same DB path so we can access what you already ingested
DB_PATH = "./fed_db"
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="fomc_minutes")

# --- FUNCTIONS ---
def get_pdf_text(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def ingest_text(text, filename):
    # Split into chunks
    chunk_size = 1000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Progress bar in UI
    progress_text = "Operation in progress. Please wait..."
    my_bar = st.progress(0, text=progress_text) #this is the progress bar, it is the progress of the operation
    
    for i, chunk in enumerate(chunks):
        response = ollama.embeddings(model='nomic-embed-text', prompt=chunk)
        collection.add(
            ids=[f"{filename}_{i}"],
            embeddings=[response['embedding']],
            documents=[chunk]
        )
        # Update progress bar
        percent_complete = (i + 1) / len(chunks)
        my_bar.progress(percent_complete, text=f"Memorizing chunk {i+1}/{len(chunks)}") #this is the progress bar, it is updated as the operation progresses
    
    my_bar.empty() #this is the progress bar, it is empty when the operation is successful
    st.success(f"✅ Processed {filename} successfully!") #this is the success message, it is displayed when the operation is successful

def analyze_sentiment(question):
    # 1. Retrieve
    response = ollama.embeddings(model='nomic-embed-text', prompt=question)
    results = collection.query(
        query_embeddings=[response['embedding']],
        n_results=5
    )
    context = "\n\n".join(results['documents'][0])
    
    # 2. Generate
    system_prompt = "You are a specialized Financial Analyst. Be concise and professional."
    user_prompt = f"""
    Based on the following FOMC Minutes excerpts:
    {context}
    
    Answer this question: {question}
    
    If the question asks for sentiment, classify it as HAWKISH, DOVISH, or NEUTRAL and explain why using quotes.
    """
    
    output = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ])
    return output['message']['content']

# --- SIDEBAR (Upload) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1a/Seal_of_the_United_States_Federal_Reserve_System.svg", width=100)
    st.title("🦅 Fed Watcher")
    st.markdown("Upload a new Fed Minute PDF to analyze it, or chat with existing data.")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process PDF"): #this is the button that processes the pdf
            with st.spinner("Reading PDF..."): #this is the spinner, it is displayed while the operation is in progress
                raw_text = get_pdf_text(uploaded_file)
                ingest_text(raw_text, uploaded_file.name) #this is the function that ingests the text into the database

# --- MAIN PAGE ---
st.title("🏦 AI Monetary Policy Analyst")
st.caption("Powered by Llama 3.1 & RAG (Running Locally on RX 6700 XT)")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello Samuel. I have read the Fed minutes. Ask me about inflation, interest rates, or the general sentiment."}]

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input
if prompt := st.chat_input("Ask about the Fed's stance..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Generate response
    with st.spinner("Thinking..."):
        response_text = analyze_sentiment(prompt)
    
    # Add AI message to state
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.chat_message("assistant").write(response_text)