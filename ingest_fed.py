import os
import ollama
import chromadb
from pypdf import PdfReader

# 1. Setup Database
# We use a persistent database so the data survives after the script finishes
db_path = "./fed_db"
client = chromadb.PersistentClient(path=db_path) #this is the database, persistent client stores data on the disk vs in memory
collection = client.get_or_create_collection(name="fomc_minutes") #this is the collection, it is a group of documents inside the database

# 2. Helper to read PDF
def load_pdf(directory): #this function reads the pdf files and extracts the text
    text_data = []
    # Find all PDFs in the data folder
    for filename in os.listdir(directory): #this loops through the files in the directory
        if filename.endswith(".pdf"): #this checks if the file is a pdf
            filepath = os.path.join(directory, filename) #this creates a string path to the file, this is the destination location
            print(f"📖 Reading: {filename}...") 
            reader = PdfReader(filepath)
            text = "" #this initializes the text variable
            for page in reader.pages: #this loops through the pages in the pdf
                text += page.extract_text() #this extracts the text from the page
            text_data.append({"filename": filename, "text": text}) #this adds the text to the text_data list
    return text_data

# 3. Main Logic
if __name__ == "__main__":
    print("--- Starting Ingestion ---")
    
    # Load PDF text
    documents = load_pdf("./data")
    
    if not documents:
        print("❌ No PDFs found in ./data folder!")
        exit()

    # Clear old data (optional, but good for testing so we don't duplicate)
    # collection.delete(where={}) 

    for doc in documents:
        full_text = doc["text"]
        filename = doc["filename"]
        
        # Split text into chunks (approx 1000 chars overlap slightly)
        chunk_size = 1000
        overlap = 100
        chunks = []
        for i in range(0, len(full_text), chunk_size - overlap):
            chunks.append(full_text[i:i + chunk_size])
        
        print(f"🧩 Splitting {filename} into {len(chunks)} chunks...")

        # Embed and Store
        for i, chunk in enumerate(chunks):
            # Generate vector using 'nomic-embed-text' (The "Translator")
            response = ollama.embeddings(model='nomic-embed-text', prompt=chunk) #this generates a vector for the chunk
            embedding = response['embedding'] #this is the vector for the chunk
            
            # Add to ChromaDB
            collection.add(
                ids=[f"{filename}_chunk_{i}"], #this is the id of the chunk
                embeddings=[embedding],
                documents=[chunk], #this is the text of the chunk
                metadatas=[{"source": filename}]
            )
            print(f"   Saved chunk {i+1}/{len(chunks)}", end="\r")
        print("\n")

    print(f"✅ Success! Data stored in {db_path}")