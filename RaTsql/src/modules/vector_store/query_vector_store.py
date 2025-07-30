# -*- coding: utf-8 -*-
# File    : query_vector_store.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 6:30 PM

from langchain_milvus import Milvus

def get_similar_queries(_vector_store: Milvus, comparison_query: str, top_k: int):
    try:
        if not isinstance(_vector_store, Milvus):
            raise TypeError(f"Expected 'vector_store' to be a Milvus instance, got {type(_vector_store).__name__} instead.")

        return _vector_store.similarity_search_with_score(query=comparison_query, k=top_k)
    except Exception as e:
        raise Exception(f"Error while searching similar query from vectory db : {e}")

if __name__ == "__main__":
    DEEPINFRA_API_TOKEN = "xxx"
    to_search = "What are my top performing campaigns ?"

    import pprint
    from milvus_client import get_milvus_vector_store
    from embed_model import get_deepinfra_embedding_model

    # Embedding Model
    embedding_model = get_deepinfra_embedding_model(DEEPINFRA_API_TOKEN=DEEPINFRA_API_TOKEN,
                                                    embd_model="BAAI/bge-en-icl")
    vector_store = get_milvus_vector_store(embedding_model=embedding_model)
    results = get_similar_queries(_vector_store=vector_store, comparison_query=to_search, top_k=2)

    similar_data_query = {}
    for i, (doc, score) in enumerate(results):
        # print(f"doc = {doc}")
        # print(f"score = {score}")
        # break
        if score > 0.3:
            if i == 0:
                print("routing through RAG")
            stored_query = doc.page_content
            cosine_score = score
            query_path = doc.metadata['query_path']
            ref_id = doc.metadata['ref_id']
            # similar_data_query[f"q{i}"] = [stored_query, cosine_score, query_path, ref_id]
            similar_data_query[f"q{i}"] = {
                "query": stored_query,
                "score": cosine_score,
                "metadata_path": query_path,
                "ref_id": ref_id
            }
        pprint.pp(f"similar_data_query = {similar_data_query}")
        # pprint.pp(f"* [SIM={score}]")
        # pprint.pp(f"content = {doc.page_content}")
        # pprint.pp(f"metadata =  [{doc.metadata}]")
        # print("-------------------------------------------")
