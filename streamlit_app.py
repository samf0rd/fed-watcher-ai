import streamlit as st
import openai
import chromadb
import plotly.graph_objects as go
import os
import re
import sys

# --- CHROMA DB HACK FOR STREAMLIT CLOUD ---
# Streamlit Cloud runs on Linux with an old SQLite version.
# This forces it to use the newer pysqlite3-binary installed in requirements.txt
if 'linux' in sys.platform:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fed Watcher Pro", page_icon="🦅", layout="wide")

# --- API SETUP ---
# We get the API key from Streamlit Secrets (secure cloud storage)
# Locally, you can make a .streamlit/secrets.toml file
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API Key is missing! Please set it in Streamlit Secrets.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# --- SETUP BACKEND ---
# Ensure your ./fed_db folder is uploaded to GitHub!
DB_PATH = "./fed_db"
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="fomc_minutes")

# --- HELPER FUNCTIONS ---

def get_meeting_list():
    """Scans the ./data folder (uploaded to GitHub) for PDFs."""
    if not os.path.exists("./data"):
        return []
    files = [f for f in os.listdir("./data") if f.endswith(".pdf")]
    files.sort(reverse=True)
    return files

def get_hawk_dove_score(text_context):
    """Asks GPT-4o-mini to rate the sentiment."""
    system_prompt = """
    You are a Quantitative Financial Analyst. 
    Your task is to analyze Federal Reserve minutes and assign a 'Hawkishness Score'.
    
    Scale:
    0 = Extremely Dovish (lowering rates, stimulating economy)
    50 = Neutral
    100 = Extremely Hawkish (raising rates, fighting inflation)
    
    Output Format:
    You must output strictly in this format:
    SCORE: [number]
    REASON: [One sentence explanation]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Analyze this text and give a score:\n\n{text_context[:10000]}"} 
        ],
        temperature=0
    )
    
    content = response.choices[0].message.content
    
    match = re.search(r'SCORE:\s*(\d+)', content)
    score = int(match.group(1)) if match else 50
    reason = content.split("REASON:")[-1].strip() if "REASON:" in content else content
    
    return score, reason

def make_gauge_chart(score):
    """Creates the gauge chart (Same as before)."""
    if score < 40: bar_color = "#2ecc71" 
    elif score > 60: bar_color = "#e74c3c" 
    else: bar_color = "#95a5a6" 

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Hawkishness Index", 'font': {'size': 18, 'color': 'gray'}},
        number = {'font': {'size': 40, 'weight': 'bold'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickvals': [20, 50, 80], 'ticktext': ['DOVISH', 'NEUTRAL', 'HAWKISH']},
            'bar': {'color': bar_color, 'thickness': 0.25},
            'steps': [
                {'range': [0, 40], 'color': '#ecf9f1'},
                {'range': [40, 60], 'color': '#f0f2f6'},
                {'range': [60, 100], 'color': '#fdeded'}
            ]
        }
    ))
    fig.update_layout(margin=dict(l=30, r=30, t=50, b=30), height=250, paper_bgcolor="rgba(0,0,0,0)", font={'family': "Arial"})
    return fig

def run_rag_chat(prompt, selected_file):
    """Handles the RAG process using OpenAI Embeddings."""
    with st.spinner("Analyzing documents..."):
        # 1. Embed prompt using OpenAI
        response = client.embeddings.create(input=prompt, model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
        
        # 2. Query DB
        rag_results = collection.query(
            query_embeddings=[query_embedding], 
            n_results=3, 
            where={"source": selected_file}
        )
        
        context = "\n".join(rag_results['documents'][0]) if rag_results['documents'] else "No relevant context found."
        
        # 3. Generate Answer
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {'role': 'system', 'content': f"Answer concisely using this context only: {context}"},
                {'role': 'user', 'content': prompt}
            ]
        )
        return resp.choices[0].message.content

# --- SIDEBAR & MAIN LOGIC (Keep largely the same) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1a/Seal_of_the_United_States_Federal_Reserve_System.svg", width=80)
    st.title("🦅 Fed Watcher Pro")
    st.caption("Live Cloud Version | Powered by OpenAI")
    
    available_files = get_meeting_list()
    if available_files:
        selected_file = st.selectbox("📅 Select Meeting History:", available_files)
    else:
        st.error("No data found! Ensure ./data folder is in GitHub.")
        selected_file = None

st.title("🏛️ US Federal Reserve Policy Dashboard")

if "messages" not in st.session_state:
    st.session_state.messages = []

if selected_file:
    # Logic to fetch text from DB
    results = collection.get(where={"source": selected_file}, limit=1) # Just check if exists
    
    # We need to fetch the actual text content for the sentiment analysis
    # Since we can't context-window the WHOLE PDF easily without cost, 
    # we usually grab the first N chunks or a summary if you pre-computed it.
    # For now, let's grab the first 5 chunks (~2000 words) for the score.
    full_text_results = collection.get(where={"source": selected_file}, limit=5)
    context_text = "\n".join(full_text_results['documents']) if full_text_results['documents'] else ""

    if "analyzed_file" not in st.session_state or st.session_state["analyzed_file"] != selected_file:
        with st.spinner(f"Analyzing sentiment for {selected_file}..."):
            score, reason = get_hawk_dove_score(context_text)
            st.session_state["analyzed_file"] = selected_file
            st.session_state["current_score"] = score
            st.session_state["current_reason"] = reason
            st.session_state.messages = []

    # Dashboard Columns
    col1, col2 = st.columns([1.5, 3])
    with col1:
        st.plotly_chart(make_gauge_chart(st.session_state["current_score"]), use_container_width=True)
    with col2:
        st.subheader("Analysis Summary")
        score = st.session_state["current_score"]
        status_type = "success" if score < 40 else "error" if score > 60 else "info"
        getattr(st, status_type)(st.session_state["current_reason"], icon="💡")

    st.divider()
    st.subheader("💬 Analyst Chat")

    # Chat Logic (Same as yours)
    user_input = st.chat_input("Ask a custom question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        ai_msg = run_rag_chat(user_input, selected_file)
        st.session_state.messages.append({"role": "assistant", "content": ai_msg})
        st.chat_message("assistant").write(ai_msg)

else:
    st.info("Please select a meeting from the sidebar.")