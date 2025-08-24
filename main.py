from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, PromptTemplate
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings
from llama_index.core.node_parser import SentenceSplitter
from pathlib import Path
import uvicorn
import asyncio

# This is set globally for the LlamaIndex application
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# CONFIG 
PDF_DIR = "./data"
STORAGE_DIR = "./storage"
OLLAMA_MODEL = "gemma2:2b"

# FASTAPI SETUP
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.dtforg.in", "https://dtforg.in"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM SETUP 
print("Loading LLM...")
# Increased timeout for potentially slower models on the VPS
llm = Ollama(model=OLLAMA_MODEL, request_timeout=120)

# INDEX SETUP
# This block checks if a vector store already exists.
# If not, it creates one from the PDFs in the data directory.
try:
    if not Path(STORAGE_DIR).exists():
        print("No storage found. Loading documents & building new index...")
        # Optimized chunking for better context retrieval
        parser = SentenceSplitter(chunk_size=350, chunk_overlap=35)
        documents = SimpleDirectoryReader(PDF_DIR).load_data()
        nodes = parser.get_nodes_from_documents(documents)
        # Create and persist the index
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(persist_dir=STORAGE_DIR)
        print("💾 Index built and saved to disk.")
    else:
        print("Loading saved vector index from disk...")
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
        print("✅ Index loaded successfully.")

except Exception as e:
    print(f"❌ Error during index setup: {e}")
    index = None

#  PROMPT TEMPLATE & QUERY ENGINE SETUP 
# This template instructs the model on how to behave and use the context.
qa_prompt_tmpl_str = (
    "You are a professional AI assistant for the Dattopant Thengadi Foundation. "
    "Your role is to answer questions accurately and concisely based ONLY on the provided context documents.\n"
    "If the context does not contain the answer, state that you do not have enough information.\n"
    "---------------------\n"
    "CONTEXT: {context_str}\n"
    "---------------------\n"
    "QUESTION: {query_str}\n"
    "ANSWER (be clear and helpful):"
)
qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

if index:
    # Configure the query engine with the prompt template and retrieval settings
    query_engine = index.as_query_engine(
        llm=llm,
        streaming=True,
        text_qa_template=qa_prompt_tmpl,
        similarity_top_k=3  # Retrieving only the top 3 most relevant text chunks
    )
else:
    query_engine = None

# SANITY CHECK ENDPOINT 
@app.get("/")
async def root():
    return {"message": "Backend is running. Auth: Zenoharsh"}

# API ENDPOINT FOR CHAT
# Using a semaphore to limit concurrent requests to prevent server overload
semaphore = asyncio.Semaphore(2)
@app.post("/chat")
async def chat(request: Request):
    if not query_engine:
        async def index_error_stream():
            yield "❌ Error: The document index is not available."
        return StreamingResponse(index_error_stream(), media_type="text/event-stream")

    async with semaphore:
        body = await request.json()
        question = body.get("message", "")

        # --- VALIDATION LOGIC ---
        if not question or len(question.strip()) < 2:
            async def validation_error_stream():
                yield "⚠️ Please ask a valid question."
            return StreamingResponse(validation_error_stream(), media_type="text/event-stream")

        # --- QUESTION LOGGING ---
        print(f"📥 Q: {question}")

        # --- STREAMING LOGIC FOR VALID QUESTIONS ---
        async def event_stream():
            """Generator function to stream the response for a valid question."""
            try:
                streaming_response = query_engine.query(question)
                for token in streaming_response.response_gen:
                    yield token
                    await asyncio.sleep(0.01)
            except Exception as e:
                print(f"❌ Error during streaming query: {e}")
                yield "Sorry, an error occurred while processing your request."

        return StreamingResponse(event_stream(), media_type="text/event-stream")

# LOCAL TEST RUNNER 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

