# -*- coding: utf-8 -*-
# Project : 
# File    : run_graphs.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:45 PM


from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
from global_graph import get_global_graph
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
LANGFUSE_SECRET_KEY = str(os.getenv("LANGFUSE_SECRET_KEY"))
LANGFUSE_PUBLIC_KEY = str(os.getenv("LANGFUSE_PUBLIC_KEY"))
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST
)
langfuse = get_client()
predefined_trace_id = Langfuse.create_trace_id()
langfuse_handler = CallbackHandler()


ratsql = get_global_graph()

user_config = {
    "configurable": {"thread_id": "rat_04"},
    "callbacks": [langfuse_handler],
    "session_id": "04",
    "user_id": "rat",
}
# Set trace attributes dynamically via enclosing span
with langfuse.start_as_current_span(
    name="RaTsql-graph",
) as span:
    span.update_trace(
        user_id="rat",
        session_id="04",
        tags=["testing"],
    )
    ratsql.invoke(
            {
                "messages": [("user", "hi testing")],
                "data_query": "dummy data query",
            },
            config=user_config
    )
