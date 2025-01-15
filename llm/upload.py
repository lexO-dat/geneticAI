import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------
# Configuration and setup of all the supabase variables
# -------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load all the text from a file
loader = TextLoader("my_text_file.txt")
documents = loader.load()


# -------------------------------------------------
# Spliting the text into chunks 
# -------------------------------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
docs = text_splitter.split_documents(documents)


# -------------------------------------------------
# Embedding model configuration
# -------------------------------------------------
embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="mxbai-embed-large:latest"
)

# -------------------------------------------------
# vectorstore conection
# -------------------------------------------------
vectorstore = SupabaseVectorStore.from_documents(
    docs,
    embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents" 
)

print("Done! Your text chunks are now embedded and saved to Supabase.")
