# -*- coding: utf-8 -*-
# File    : populate_vectore_space.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 4:10 PM

import os
import json
import argparse
from pathlib import Path
from langchain_core.documents import Document
from dotenv import load_dotenv, find_dotenv
from milvus_client import get_milvus_vector_store
from embed_model import get_deepinfra_embedding_model

from pathlib import Path
import json
from langchain.schema import Document


def load_json_files(base_dir: str):
    """
    Load JSON files from the specified directory and convert them into Document objects.
    Skips 'lookup_registry.json' files.

    :param base_dir: Location of the directory containing JSON files.
    :return: List of Document objects.
    """
    try:
        documents = []
        json_paths = Path(base_dir).rglob("*.json")

        for path in json_paths:
            if path.name == "lookup_registry.json":
                continue  # Skip registry files is it's lookup registry

            with open(path, "r") as f:
                data = json.load(f)
                question = data.get("query", "").strip()
                if not question:
                    continue

                metadata = {
                    "ref_id": data.get("ref_id"),
                    "query_path": str(path)
                }

                documents.append(Document(page_content=question, metadata=metadata))

        return documents

    except Exception as e:
        raise RuntimeError(f"Failed to load JSON files from {base_dir}: {str(e)}")


if __name__ == "__main__":
    load_dotenv(find_dotenv(), override=True)

    DEEPINFRA_API_TOKEN = os.getenv("DEEPINFRA_API_TOKEN")
    assert DEEPINFRA_API_TOKEN, "DEEPINFRA_API_TOKEN not found in environment"

    # TODO : change the dir to argparse
    _base_dir = "/home/prakhar/luke-dev/txt2sql_methods/RaTsql/data/metadata_query_store/"

    docs = load_json_files(base_dir=_base_dir)
    print(f"Loaded {len(docs)} documents. Inserting into vector store...")

    # Embedding Model
    embedding_model = get_deepinfra_embedding_model(DEEPINFRA_API_TOKEN=DEEPINFRA_API_TOKEN,
                                                    embd_model="BAAI/bge-en-icl")
    vector_store = get_milvus_vector_store(embedding_model=embedding_model)
    vector_store.add_documents(documents=docs)
    print("All documents inserted into Milvus.")

