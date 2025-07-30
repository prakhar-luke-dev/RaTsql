# -*- coding: utf-8 -*-
# Project : 
# File    : global_graph.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 4:29 PM

from states import GlobalState
from langgraph.types import Command
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from graphs import build_head_graph, build_body_graph, build_tail_graph
from typing import Dict
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from psycopg import Connection, OperationalError

POSTGRES_USER = "luke"
POSTGRES_PASSWORD = "luke"
POSTGRES_DB = "luke"
POSTGRES_URI = "postgres://luke:luke@localhost:5432/luke"
MEMORY_CONNECTION_KWARGS: Dict = {
        "autocommit": True,
        "prepare_threshold": 0,
    }
if not POSTGRES_URI:
    try:
        pool = Connection.connect(POSTGRES_URI, **MEMORY_CONNECTION_KWARGS)
        checkpointer = PostgresSaver(pool)
        # Only one time at init of project
        checkpointer.setup()
    except OperationalError as e:
        raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid PostgreSQL URI: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while connecting to PostgreSQL: {str(e)}")
else:
    print("POSTGRES not available using RAM for chat history (this won't be stored)")
    checkpointer = MemorySaver()

def head_subgraph(state: GlobalState):
    return build_head_graph()

def body_subgraph(state: GlobalState):
    return build_body_graph()

def tail_subgraph(state: GlobalState):
    return build_tail_graph()

def get_global_graph():
    global_graph = StateGraph(GlobalState)

    global_graph.add_node("head", head_subgraph)
    global_graph.add_node("body", body_subgraph)
    global_graph.add_node("tail", tail_subgraph)

    global_graph.add_edge(START, "head")
    global_graph.add_edge("head", "body")
    global_graph.add_edge("body", "tail")
    global_graph.add_edge("tail", END)


    ratsql_graph = global_graph.compile(checkpointer=checkpointer)
    return ratsql_graph
