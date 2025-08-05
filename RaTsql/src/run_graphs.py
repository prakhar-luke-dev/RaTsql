# -*- coding: utf-8 -*-
# Project : 
# File    : run_graphs.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:45 PM


from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

from config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST
)
from global_graph import get_global_graph

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
    "configurable": {"thread_id": "saint_luke"},
    "callbacks": [langfuse_handler],
    "session_id": "preach_channa",
    "user_id": "luke",
}
# Set trace attributes dynamically via enclosing span
with langfuse.start_as_current_span(
    name="RaTsql-graph",
) as span:
    span.update_trace(
        user_id="saint_luke",
        session_id="preach_channa",
        tags=["preaching"],
    )
    Ratsql_response = ratsql.invoke(
            {
                "messages": [("user", "hi testing")],
                "data_query": "What are the campaigns with ROAS in the top 5% over the past 14 days, and how has it changed compared to the previous week?",
                "customer_id": "1396334731",
                "max_retires_remaining": 3,
            },
            config=user_config
    )
    print(f"ANSWER FROM RaT2sql : \n{Ratsql_response}")

