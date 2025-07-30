import os
import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.embeddings import DeepInfraEmbeddings
from langchain_milvus import Milvus
from pymilvus import MilvusClient
from dotenv import load_dotenv

load_dotenv()  # Optional: If you're loading env vars from .env

DEEPINFRA_API_TOKEN = os.getenv("DEEPINFRA_API_TOKEN")
assert DEEPINFRA_API_TOKEN, "DEEPINFRA_API_TOKEN not found in environment"

# Embedding Model
embedding_model = DeepInfraEmbeddings(
    model_id="BAAI/bge-en-icl", 
    deepinfra_api_token=DEEPINFRA_API_TOKEN
)

# Milvus Vector Store
URI = "./milvus_rag_demo.db"
vector_store = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": URI, "token": "root:Milvus", "db_name": "milvus_demo"},
    index_params={"index_type": "FLAT", "metric_type": "L2"},
    collection_name="test_collection",
    collection_description="This is a testing collection for Rag demo",
)

def load_json_files(base_dir: str):
    json_paths = Path(base_dir).rglob("*.json")
    documents = []

    for path in json_paths:
        with open(path, "r") as f:
            data = json.load(f)
            question = data.get("query", "").strip()
            if not question:
                continue

            metadata = {
                "ref_id": data.get("ref_id"),
                "query_path": str(path)
            }

            doc = Document(page_content=question, metadata=metadata)
            documents.append(doc)
    
    return documents

if __name__ == "__main__":
    base_dir = "query_store/"
    docs = load_json_files(base_dir)
    print(f"📦 Loaded {len(docs)} documents. Inserting into Milvus...")

    vector_store.add_documents(docs)
    print("✅ All documents inserted into Milvus.")
