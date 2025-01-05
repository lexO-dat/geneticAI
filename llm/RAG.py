from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from supabase import create_client, Client

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
    model="llama3.2:1b"
)

# -------------------------------
# Ollama Embedding Model Configuration
# -------------------------------
embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="nomic-embed-text:latest"
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
    response = retrieval_chain.run(query)
    return response

# Example query
query = input("Query: ")
response = chat_response(query)
print(response)
