# -*- coding: utf-8 -*-
# Project :
# File    : graphs.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM


from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from states import GlobalState, HeadState, BodyState, TailState
from nodes import *
from utils import save_graph_to_file


#===========================================================================
#                                 HEAD GRAPH
#===========================================================================
#  *                                 INFO
#  
#  Aim of this graph is to generate pruned schema from RAG or full approach.  
#  1. RAG Approach : Get pruned schema from similar queries.
#  2. Full Approach : Get pruned schema from LLM by passing full schema.  
# 
#===========================================================================

def build_head_graph():
    head = StateGraph(HeadState)

    head.add_node("user_question", user_question)
    head.add_node("rag_node", rag_node)
    head.add_node("method_router_node", method_router_node)
    head.add_node("get_pruned_schema_from_rag", get_pruned_schema_from_rag)
    head.add_node("get_pruned_schema_from_full_approach", get_pruned_schema_from_full_approach)

    head.add_edge(START, "user_question")

    head_graph = head.compile(checkpointer=True)

    return head_graph


#===========================================================================
#                                 BODY GRAPH
#===========================================================================
#  *                                 INFO
#  Aim of this graph is to generate 3 different SQL queries.  
#  1. SQL1 = full schema + user question + pruned schema + other info
#  2. dense_schema = schema from SQL1 union pruned schema + other info
#  3. Hints = dense_schema + user_question + other info
#  4. SQL2 = dense_schema + hints + user_question + other info
#  5. SQL3 = SQL1 + result1 + SQL2 + result2 + user_question + other info
#  6. loop_sql3 till n times
# 
#===========================================================================

def build_body_graph():
    body = StateGraph(BodyState)

    body.add_node("get_schema_from_sql", get_schema_from_sql)
    body.add_node("gen_sql1", gen_sql1)
    body.add_node("dense_schema", dense_schema)
    body.add_node("gen_hints", gen_hints)
    body.add_node("gen_sql2", gen_sql2)
    body.add_node("execute_2sql", get_result_from_both_queries)
    body.add_node("gen_sql3", gen_sql3)
    body.add_node("rout_sql3", judge_sql3)
    body.add_node("modify_sql3", modify_sql3)
    body.add_node("final_answer", final_answer)

    body.add_edge(START, "gen_sql1")

    body_graph = body.compile(checkpointer=True)

    return body_graph



#===========================================================================
#                                 TAIL GRAPH
#===========================================================================
#  *                                 INFO
#  Aim of this graph is to populate RAG with the positve feedback and send
#  negative to the developer to tune the approach.
#    
#    
# 
#===========================================================================

def build_tail_graph():
    tail = StateGraph(TailState)

    tail.add_node("feedback_router", feedback_router)
    tail.add_node("feedback_node", feedback_node)
    tail.add_node("positive", positive)
    tail.add_node("negative", negative)
    tail.add_node("verify_feedback", verify_feedback)
    tail.add_node("send_to_dev_to_tune_approach", send_to_dev_to_tune_approach)
    tail.add_node("store_in_rag", store_in_rag)

    tail.add_edge(START, "feedback_router")

    tail_graph = tail.compile(checkpointer=True)
    return tail_graph


# save_graph_to_file(runnable_graph=build_head_graph(), output_file_path="head_graph")
# save_graph_to_file(runnable_graph=build_body_graph(), output_file_path="body_graph")
# save_graph_to_file(runnable_graph=build_tail_graph(), output_file_path="tail_graph")