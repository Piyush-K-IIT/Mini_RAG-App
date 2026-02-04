import streamlit as st
from pinecone import Pinecone, ServerlessSpec
import uuid
import time
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import cohere

# --- 1. CONFIGURATION & API KEYS ---
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
COHERE_API_KEY = st.secrets["COHERE_API_KEY"]

# --- 2. INITIALIZE CLIENTS ---
st.set_page_config(page_title="Mini RAG App", layout="wide")
st.title("🤖 Mini RAG Assessment App ")

pc = Pinecone(api_key=PINECONE_API_KEY)
# CHANGED: New index name to force a clean environment
index_name = "gemini-final-index" 
GEMINI_DIMENSION = 768 

# --- ROBUST INDEX MANAGEMENT ---
existing_indexes = [idx.name for idx in pc.list_indexes()]

if index_name in existing_indexes:
    desc = pc.describe_index(index_name)
    if desc.dimension != GEMINI_DIMENSION:
        st.warning(f"Recreating Index: Switching from {desc.dimension}D to {GEMINI_DIMENSION}D...")
        pc.delete_index(index_name)
        time.sleep(15) # Wait for cloud propagation

if index_name not in [idx.name for idx in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=GEMINI_DIMENSION,
        metric='cosine', 
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
    st.success("Clean 768D Index Ready!")

index = pc.Index(index_name)

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=GOOGLE_API_KEY
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Use the 2026 stable version
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)
co = cohere.Client(api_key=COHERE_API_KEY)

# --- 3. DOCUMENT INGESTION ---
st.header("1. Upload & Index Document")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file and st.button("Index Document"):
    with st.spinner("Processing PDF and Upserting to Pinecone..."):
        try:
            reader = PdfReader(uploaded_file)
            # Extract text and handle empty pages
            pages_text = [page.extract_text() for page in reader.pages if page.extract_text()]
            raw_text = "".join(pages_text)
            
            if not raw_text:
                st.error("Could not extract text from this PDF. Is it a scanned image?")
                st.stop()

            # Text Cleaning
            text = raw_text.encode("ascii", "ignore").decode("ascii")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=600, 
                chunk_overlap=50
            )
            chunks = text_splitter.split_text(text)
            st.write(f"Created {len(chunks)} chunks. Starting embeddings...")

            vectors_to_upsert = []
            for i, chunk in enumerate(chunks):
                # IMPORTANT: Ensure the embedding model is actually returning a vector
                vector = embeddings_model.embed_query(chunk)
                
                metadata = {
                    "text": chunk.strip(), 
                    "source": str(uploaded_file.name), 
                    "chunk_id": i
                }
                
                vectors_to_upsert.append((f"id-{i}", vector, metadata))
            
            # THE CRITICAL PART: Check if list is empty before upserting
            if vectors_to_upsert:
                # Upsert in one go for small documents
                index.upsert(vectors=vectors_to_upsert)
                st.success(f"✅ Successfully sent {len(vectors_to_upsert)} records to Pinecone!")
                st.info("Wait 20 seconds for the Dashboard to update.")
            else:
                st.error("No vectors were generated. Check your Google API Key.")
            
        except Exception as e:
            st.error(f"Error during indexing: {str(e)}")

st.divider()

# --- 4. QUERY, RERANK, & ANSWER ---
st.header("2. Ask a Question")
user_query = st.text_input("Enter your question:")

if user_query:
    start_time = time.time()
    with st.spinner("Searching and Reranking..."):
        query_vector = embeddings_model.embed_query(user_query)
        initial_results = index.query(vector=query_vector, top_k=10, include_metadata=True)
        
        if not initial_results['matches']:
            st.error("No relevant context found. Try waiting a few seconds.")
        else:
            documents_to_rerank = [match['metadata']['text'] for match in initial_results['matches']]
            
            rerank_results = co.rerank(
                query=user_query,
                documents=documents_to_rerank,
                top_n=3,
                model="rerank-english-v3.0"
            )
            
            final_context = [documents_to_rerank[hit.index] for hit in rerank_results.results]
            
            prompt = f"""
            Use the context below to answer. If not in context, say you don't know. 
            Use inline citations like [1], [2].
            
            Context:
            {chr(10).join([f"[{i+1}] {text}" for i, text in enumerate(final_context)])}
            
            Question: {user_query}
            """
            
            response = llm.invoke(prompt)
            st.subheader("Final Answer")
            st.write(response.content)
            
            with st.expander("View Reranked Sources"):
                for i, doc in enumerate(final_context):
                    st.markdown(f"**Source [{i+1}]**")
                    st.write(doc)




