import ollama
import chromadb

# 1. Connect to the same database
client = chromadb.PersistentClient(path="./fed_db")
collection = client.get_or_create_collection(name="fomc_minutes")

# 2. Define the "Analyst" Persona
SYSTEM_PROMPT = """
You are a Senior Macroeconomic Analyst for a major bank. 
Your job is to analyze Federal Reserve minutes and determine the sentiment.
You must classify the sentiment as: HAWKISH, DOVISH, or NEUTRAL.
Only use the provided context to answer. If the context is missing, say so.
"""

def analyze_sentiment(question):
    print(f"\n🔎 Searching minutes for topics related to: '{question}'...")
    
    # A. Search the DB for relevant chunks (Retrieval)
    # We turn the question into a vector and find the closest matching chunks
    response = ollama.embeddings(model='nomic-embed-text', prompt=question)
    query_embedding = response['embedding']
    
    results = collection.query( #this is the query, it is the question for the model
        query_embeddings=[query_embedding], #this is the vector for the question
        n_results=5  # Retrieve top 5 most relevant chunks
    ) #this is the results, it is the chunks that are most relevant to the question
    
    # Combine the found chunks into one block of text
    retrieved_context = "\n\n".join(results['documents'][0]) #this is the text of the chunks that are most relevant to the question
    
    # B. Ask Llama 3.1 (Generation)
    print("🧠 Analyzing sentiment...")
    prompt = f"""
    Context from FOMC Minutes:
    {retrieved_context}
    
    User Question: {question}
    
    Task: 
    1. Summarize what the Fed said about this topic.
    2. Classify the sentiment (Hawkish/Dovish/Neutral).
    3. Quote the specific sentence that supports your classification.
    """
    
    output = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT}, #this is the system prompt, it is the instructions for the model
        {'role': 'user', 'content': prompt} #this is the user prompt, it is the question for the model
    ])
    
    return output['message']['content'] #this is the answer from the model

if __name__ == "__main__":
    # The big question for the portfolio
    question = "What is the committee's stance on inflation and future interest rate hikes?"
    
    analysis = analyze_sentiment(question)
    
    print("\n" + "="*40)
    print("🦅 FED WATCHER AI REPORT")
    print("="*40 + "\n")
    print(analysis)