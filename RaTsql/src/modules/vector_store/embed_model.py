# -*- coding: utf-8 -*-
# File    : embed_model.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 4:56 PM

from langchain_community.embeddings import DeepInfraEmbeddings


def get_deepinfra_embedding_model(*, DEEPINFRA_API_TOKEN: str, embd_model: str ="BAAI/bge-en-icl"):
    try:
        if not DEEPINFRA_API_TOKEN:
            raise ValueError("DEEPINFRA_API_TOKEN is required and cannot be empty.")
        embedding_model = DeepInfraEmbeddings(
            model_id=embd_model,
            deepinfra_api_token=DEEPINFRA_API_TOKEN
        )
        return embedding_model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize DeepInfraEmbeddings : {e}")