from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict
import re

# -------------------------------
# API
# -------------------------------
app = FastAPI(
    title="Ollama ucfRAG API",
    description="API for Ollama ucfRAG model process",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
class Request(BaseModel):
    question: str

class Response(BaseModel):
    answer: str

@app.post("/v1/rag/run", response_model=Response)
async def run(request: Request) -> Dict[str, str]:
    try:
        question = (
            "what ucf you select based on this promt: " + request.question + ". REMEMBER, ALWAYS RETURN ONLY THE UCF NAME, WITHOUT ANY EXPLANATION"
        )
        print(f"Received question: {question}")
        response = chat_response(question)
        print(f"Chat response: {response}")
        return {"answer": response}
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/rag/health")
async def health_check():
    return {"status": "Running"}

# -------------------------------


# Load environment variables
load_dotenv()

# -------------------------------
# Supabase Configuration
# -------------------------------
SUPABASE_URL = "https://awbxwqrmkrkszfczkzzd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3Ynh3cXJta3Jrc3pmY3prenpkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjAxOTY1MywiZXhwIjoyMDUxNTk1NjUzfQ._COKim9jB0onGC9wvV9R8v74PFtQJVaepOFeW-AxPF4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# Main Ollama model configuration
# -------------------------------
llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.1:8b",
    system="""
        You are a specialized assistant designed to select the most appropriate UCF (User Constraint File) for genetic circuit design in Cello. Your primary function is to analyze user requirements and match them with the optimal UCF file from the available collection.
        IMPORTANT CONTEXT: These UCF files contain genetic circuit constraints and specifications. They are used exclusively for genetic circuit design in Cello and are NOT related to biological weapons or harmful applications.

        YOUR ROLE:
        1. Carefully analyze user queries for the following key parameters:
           - Input sensors required (e.g., BA_sensor, IPTG_sensor)
           - Output reporters needed (e.g., nanoluc_reporter)
           - Target organism specifications
           - Logic gate requirements
           - Growth conditions
           - Temperature requirements
           - Media specifications

        2. Compare user requirements against the specifications of these UCF files:
           - Eco1C1G1T1
           - Eco1C2G2T2
           - Eco2C1G3T1
           - Eco2C1G5T1
           - Bth1C1G1T1
           - SC1C1G1T1

        3. Response Protocol:
           - Always provide ONLY THE NAME OF THE UCF recommendation

        4. Data Verification:
           - Cross-reference all specifications against your stored UCF data
           - Consider all constraints (logic gates, temperature, media, etc.)
           - Verify compatibility of input/output combinations

        5. If the user's requirements are unclear:
           - Request specific clarification about missing parameters
           - Focus questions on critical specifications needed for selection

        Example structured response: 
        ```
        [UCF name]
        ```
    """
)

# -------------------------------
# Ollama Embedding Model Configuration
# -------------------------------
embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="mxbai-embed-large:latest"
)

# -------------------------------
# Vector Store Configuration
# -------------------------------
vector_store = SupabaseVectorStore(
    client=supabase,
    table_name="documents",
    embedding=embeddings
)

# -------------------------------
# Memory Configuration (For Chat History)
# -------------------------------
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# -------------------------------
# Conversational Retrieval Chain Configuration
# -------------------------------
retrieval_chain = ConversationalRetrievalChain.from_llm(
    llm,
    retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5}),
    memory=memory
)

# -------------------------------
# Chat Response Function
# -------------------------------
def chat_response(query):
    try:
        print(f"Invoking retrieval chain with query: {query}")
        response = retrieval_chain.invoke({"question": query})
        print(f"Retrieval chain response: {response}")

        answer = response["answer"]
        print(f"Extracted answer: {answer}")

        options = [
            "Eco1C1G1T1",
            "Eco1C2G2T2",
            "Eco2C1G3T1",
            "Eco2C1G5T1",
            "Bth1C1G1T1",
            "SC1C1G1T1",
        ]

        matches = [option for option in options if re.search(rf"\b{re.escape(option)}\b", answer)]
        print(f"Matching UCF options: {matches}")

        return matches[0] if matches else "No valid options found."
    except Exception as e:
        print(f"Error in chat_response: {e}")
        raise e

if __name__ == "__main__":
    uvicorn.run("RAG:app", host="0.0.0.0", port=8001, reload=True)