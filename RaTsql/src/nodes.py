# -*- coding: utf-8 -*-
# Project :
# File    : nodes.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM


from states import GlobalState, HeadState, BodyState, TailState
from langgraph.types import Command
from typing import Annotated, Literal

#===========================================================================
#                            HEAD NODES
#===========================================================================

head_state_to_update = {
    "similar_data_query": {
        "q1": ["similar_data_query1", "score 0.1", "sql query", "instructions"],
        "q2": ["similar_data_query2", "score 0.45", "sql query", "instructions123"],
    },
    "similarity_threshold": 0.65,
    "rout_schema_through_rag": True,
    "pruned_schema": {"table123": ["column1", "email"]},
}

def user_question(state: HeadState) -> Command[Literal["rag_node"]]:
    print("inside head")
    return Command(
        update=head_state_to_update,
        goto="rag_node"
    )
def rag_node(state: HeadState) -> Command[Literal["method_router_node"]]:
    return Command(
        update=head_state_to_update,
        goto="method_router_node"
    )


def method_router_node(state: HeadState) -> Command[Literal["get_pruned_schema_from_rag", "get_pruned_schema_from_full_approach"]]:
    goto_node = "get_pruned_schema_from_rag" if state.get("rout_schema_through_rag") else "get_pruned_schema_from_full_approach"
    return Command(
        update=head_state_to_update,
        goto=goto_node
    )

def get_pruned_schema_from_rag(state: HeadState) -> Command[Literal["__end__"]]:
    return Command(
        update=head_state_to_update,
        goto="__end__"
    )

def get_pruned_schema_from_full_approach(state: HeadState) -> Command[Literal["__end__"]]:
    return Command(
        update=head_state_to_update,
        goto="__end__"
    )



#===========================================================================
#                            BODY NODES
#===========================================================================

body_state_to_update = {
    "dense_schema": {"table1": "col1, col2", "table2" : "col1, col4"},
    "hints" : {"element": "table1.col1", "condition": "table1.col2 > 10", "keywords": "Group By"},
    "gen_sql1": "gen_sql1",
    "res_sql1": "res_sql1",
    "gen_sql2": "gen_sql2",
    "res_sql2": "res_sql2",
    "gen_sql3": "gen_sql3",
    "res_sql3": "res_sql3",
    "final_answer": "final_answer",
}
def gen_sql1(state: BodyState) -> Command[Literal["get_schema_from_sql", "gen_sql3"]]:
    print("inside body")
    return Command(
        update=body_state_to_update,
        goto="get_schema_from_sql"
    )

def get_schema_from_sql(state: BodyState) -> Command[Literal["dense_schema"]]:
    return Command(
        update=body_state_to_update,
        goto="dense_schema"
    )

def dense_schema(state: BodyState) -> Command[Literal["gen_hints"]]:
    return Command(
        update=body_state_to_update,
        goto="gen_hints"
    )

def gen_hints(state: BodyState) -> Command[Literal["gen_sql2"]]:
    return Command(
        update=body_state_to_update,
        goto="gen_sql2"
    )

def gen_sql2(state: BodyState) -> Command[Literal["gen_sql3"]]:
    return Command(
        update=body_state_to_update,
        goto="gen_sql3"
    )

def gen_sql3(state: BodyState) -> Command[Literal["loop_sql"]]:
    return Command(
        update=body_state_to_update,
        goto="loop_sql"
    )

def loop_sql(state: BodyState) -> Command[Literal["final_answer"]]:
    return Command(
        update=body_state_to_update,
        goto="final_answer"
    )

def final_answer(state: BodyState) -> Command[Literal["__end__"]]:
    return Command(
        update=body_state_to_update,
        goto="__end__"
    )





#===========================================================================
#                            TAIL NODES
#===========================================================================

tail_state_to_update = {
    "need_feedback" : True,
    "feedback_category" : True,
    "feedback_messsage" : "dummy feedback message"
}

def feedback_router(state: TailState) -> Command[Literal["feedback_node", "__end__"]]:
    print("inside tail")
    return Command(
        update=tail_state_to_update,
        goto="feedback_node"
    )

def feedback_node(state: TailState) -> Command[Literal["positive", "negative"]]:
    return Command(
        update=tail_state_to_update,
        goto="positive"
    )
def positive(state: TailState) -> Command[Literal["verify_feedback"]]:
    return Command(
        update=tail_state_to_update,
        goto="verify_feedback"
    )
def negative(state: TailState) -> Command[Literal["send_to_dev_to_tune_approach"]]:
    return Command(
        update=tail_state_to_update,
        goto="send_to_dev_to_tune_approach"
    )

def verify_feedback(state: TailState) -> Command[Literal["store_in_rag"]]:
    return Command(
        update=tail_state_to_update,
        goto="store_in_rag"
    )
def send_to_dev_to_tune_approach(state: TailState) -> Command[Literal["__end__"]]:
    return Command(
        update=tail_state_to_update,
        goto="__end__"
    )
def store_in_rag(state: TailState) -> Command[Literal["__end__"]]:
    return Command(
        update=tail_state_to_update,
        goto="__end__"
    )
