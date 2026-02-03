# RUN THIS LOCALLY: streamlit run app_local_ollama.py

import streamlit as st
import ollama
import chromadb
import plotly.graph_objects as go
import os
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fed Watcher Pro", page_icon="🦅", layout="wide")

# --- CUSTOM CSS (For cleaner look) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# --- SETUP BACKEND ---
DB_PATH = "./fed_db"
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="fomc_minutes")

# --- HELPER FUNCTIONS ---

def get_meeting_list():
    """Scans the ./data folder to find available meetings."""
    if not os.path.exists("./data"):
        return []
    files = [f for f in os.listdir("./data") if f.endswith(".pdf")]
    files.sort(reverse=True)
    return files

def get_hawk_dove_score(text_context):
    """Asks Llama 3 to rate the sentiment on a scale of 0-100."""
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
    
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Analyze this text and give a score:\n\n{text_context[:5000]}"} 
    ])
    
    content = response['message']['content']
    
    # Extract using Regex
    match = re.search(r'SCORE:\s*(\d+)', content)
    score = int(match.group(1)) if match else 50
    reason = content.split("REASON:")[-1].strip() if "REASON:" in content else content
    
    return score, reason

def make_gauge_chart(score):
    """Creates a professional, compact financial gauge."""
    
    # Determine color based on score for the pointer/bar
    if score < 40: bar_color = "#2ecc71" # Green
    elif score > 60: bar_color = "#e74c3c" # Red
    else: bar_color = "#95a5a6" # Gray

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Hawkishness Index", 'font': {'size': 18, 'color': 'gray'}},
        number = {'font': {'size': 40, 'weight': 'bold'}},
        gauge = {
            'axis': {
                'range': [None, 100],
                'tickwidth': 2,
                'tickcolor': "white",
                # THE NEW LABELS!
                'tickvals': [20, 50, 80],
                'ticktext': ['DOVISH', 'NEUTRAL', 'HAWKISH'],
                'tickfont': {'size': 14}
            },
            'bar': {'color': bar_color, 'thickness': 0.25}, # Dynamic pointer color
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#f0f2f6",
            'steps': [
                # Softer financial colors
                {'range': [0, 40], 'color': '#ecf9f1'},  # Soft Green zone
                {'range': [40, 60], 'color': '#f0f2f6'},  # Soft Gray zone
                {'range': [60, 100], 'color': '#fdeded'} # Soft Red zone
            ],
            # Removed the threshold line for a cleaner look
        }
    ))
    
    # Make it compact by removing huge whitespace margins
    fig.update_layout(
        margin=dict(l=30, r=30, t=50, b=30),
        height=250, # Fixed small height
        paper_bgcolor="rgba(0,0,0,0)", # Transparent background
        font={'family': "Arial"}
    )
    return fig

def run_rag_chat(prompt, selected_file):
    """Handles the full RAG process for a user query."""
    with st.spinner("Thinking..."):
        # Embed prompt
        response = ollama.embeddings(model='nomic-embed-text', prompt=prompt)
        query_embedding = response['embedding']
        
        # Query DB
        rag_results = collection.query(
            query_embeddings=[query_embedding], 
            n_results=3, 
            where={"source": selected_file}
        )
        
        # Extract context
        context = "\n".join(rag_results['documents'][0]) if rag_results['documents'] else "No relevant context found."
        
        # Generate answer
        resp = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': f"Answer concisely using this context only: {context}"},
            {'role': 'user', 'content': prompt}
        ])
        return resp['message']['content']

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1a/Seal_of_the_United_States_Federal_Reserve_System.svg", width=80)
    st.title("🦅 Fed Watcher Pro")
    st.caption("This bot will analyze a chosen FOMC meeting, provide a summary and answer any questions about it.")
    
    st.divider()
    
    available_files = get_meeting_list()
    if available_files:
        selected_file = st.selectbox("📅 Select Meeting History:", available_files)
    else:
        st.error("No data found! Run scrape_history.py.")
        selected_file = None
    
    st.divider()
    st.markdown("Based on Llama 3.1 running locally on Radeon RX 6700 XT.")

# --- MAIN PAGE ---
st.title(" US Federal Reserve Policy Dashboard")

if selected_file:
    # 1. Retrieve & Analyze (Auto-refresh logic)
    results = collection.get(where={"source": selected_file}, limit=8)
    if results['documents']:
        context_text = "\n".join(results['documents'][0])
        
        if "analyzed_file" not in st.session_state or st.session_state["analyzed_file"] != selected_file:
            with st.spinner(f"Analyzing sentiment for {selected_file}..."):
                score, reason = get_hawk_dove_score(context_text)
                st.session_state["analyzed_file"] = selected_file
                st.session_state["current_score"] = score
                st.session_state["current_reason"] = reason
                st.session_state.messages = [] # Reset chat on new file

        # 2. Dashboard Layout (Adjusted ratios for a smaller gauge)
        # Using [1.5, 3] ratio makes the left column smaller than before
        col1, col2 = st.columns([1.5, 3])
        
        with col1:
            # The New Gauge
            st.plotly_chart(make_gauge_chart(st.session_state["current_score"]), use_container_width=True)
        
        with col2:
            st.subheader("Analysis Summary")
            # Using a colored box based on sentiment
            score = st.session_state["current_score"]
            if score < 40: status_type = "success" # Green
            elif score > 60: status_type = "error" # Red
            else: status_type = "info" # Blue/Gray
            
            getattr(st, status_type)(st.session_state["current_reason"], icon="💡")
            st.caption(f"Source: `{selected_file}`")

        st.divider()
        
        # 3. Chat Interface with Suggestions
        st.subheader("💬 Analyst Chat")

        # --- NEW: SUGGESTION BUTTONS ---
        # We create 3 columns above the chat input
        s_col1, s_col2, s_col3 = st.columns(3)
        suggested_prompt = None
        
        # Define the questions
        q1 = "What is the stance on inflation?"
        q2 = "How tight is the labor market?"
        q3 = "Are future rate hikes likely?"

        # Check if buttons are clicked
        if s_col1.button("📈 " + q1): suggested_prompt = q1
        if s_col2.button("🧑‍💼 " + q2): suggested_prompt = q2
        if s_col3.button("⚖️ " + q3): suggested_prompt = q3

        # Display History
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # Handle Input (Either from buttons OR text box)
        # We check suggested_prompt first. If it exists, we prioritize it.
        user_input = st.chat_input("Ask a custom question...")
        
        final_prompt = suggested_prompt if suggested_prompt else user_input

        if final_prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": final_prompt})
            st.chat_message("user").write(final_prompt)
            
            # Get AI response
            ai_msg = run_rag_chat(final_prompt, selected_file)
            
            # Add AI message
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            st.chat_message("assistant").write(ai_msg)
            
            # Force a rerun if a button was clicked so the chat updates immediately
            if suggested_prompt:
                st.rerun()

    else:
        st.warning(f"File found but not ingested: {selected_file}. Please re-run ingestion.")