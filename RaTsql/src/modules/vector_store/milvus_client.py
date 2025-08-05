# -*- coding: utf-8 -*-
# File    : milvus_client.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 4:15 PM

from langchain_milvus import Milvus

def get_milvus_vector_store(
        embedding_model,
        MILVUS_DB_NAME="milvus_ratsql_demo",
        MILVUS_COLLECTION_NAME = "ratsql_demo",
        MILVUS_COLLECTION_NAME_DESCRIPTION = "Demo collection for ratsql with Milvus"
        ):
    MILVUS_URI = f"/home/prakhar/luke-dev/txt2sql_methods/RaTsql/data/{MILVUS_DB_NAME}.db"
    # Milvus Vector Store
    milvus_vector_store = Milvus(
        embedding_function=embedding_model,
        connection_args={"uri": MILVUS_URI, "token": "root:Milvus", "db_name": MILVUS_DB_NAME},
        index_params={"index_type": "FLAT", "metric_type": "COSINE"},
        collection_name=MILVUS_COLLECTION_NAME,
        collection_description=MILVUS_COLLECTION_NAME_DESCRIPTION,

    )
    return milvus_vector_store
