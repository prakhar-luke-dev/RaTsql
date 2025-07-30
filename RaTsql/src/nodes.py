# -*- coding: utf-8 -*-
# Project :
# File    : nodes.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM

import json
import statistics

from langchain_core.messages import HumanMessage

from states import GlobalState, HeadState, BodyState, TailState
from langgraph.types import Command
from typing import Annotated, Literal
from modules.vector_store.embed_model import get_deepinfra_embedding_model
from modules.vector_store.milvus_client import get_milvus_vector_store
from modules.vector_store.query_vector_store import get_similar_queries
from utils import get_pruned_schema, union_schemas, execute_sql_query
from config import DEEPINFRA_API_TOKEN
from modules.sql_gen.sql1 import generate_sql1
from modules.prepare_data.prepare_metadata import extract_table_column_map
from modules.sql_gen.hint_gen import generate_hints_for_sql2
from modules.sql_gen.sql2 import generate_sql2
from modules.sql_gen.sql3 import generate_sql3
from modules.sql_gen.loop_sql3 import loop_sql3
#===========================================================================
#                            HEAD NODES
#===========================================================================


def user_question(state: HeadState) -> Command[Literal["rag_node"]]:
    print("inside head")
    # Setting up the similarity threshold
    head_state_to_update = {'similarity_threshold': 0.40}
    # set up the threshold and other state variables
    return Command(
        update=head_state_to_update,
        goto="rag_node"
    )

def rag_node(state: HeadState) -> Command[Literal["method_router_node"]]:
    """
    RAG node to find similar queries in the vector store based on data query.
    """
    head_state_to_update = {}
    data_query = state.get('data_query')
    embedding_model = get_deepinfra_embedding_model(DEEPINFRA_API_TOKEN=DEEPINFRA_API_TOKEN,
                                                    embd_model="BAAI/bge-en-icl")
    vector_store = get_milvus_vector_store(embedding_model=embedding_model)
    results = get_similar_queries(_vector_store=vector_store, comparison_query=data_query, top_k=5)
    similar_data_query = {}
    for i, (doc, score) in enumerate(results):
        if score > state.get("similarity_threshold"):
            if i == 0:
                head_state_to_update['rout_schema_through_rag'] = True
            stored_query = doc.page_content
            cosine_score = score
            query_path = doc.metadata['query_path']
            ref_id = doc.metadata['ref_id']
            similar_data_query[f"q{i}"] = {
                "query": stored_query,
                "score": cosine_score,
                "metadata_path": query_path,
                "ref_id": ref_id
            }
    if not similar_data_query:
        raise ValueError("No similar queries found with the given threshold.")
    head_state_to_update["similar_data_query"] = similar_data_query

    return Command(
        update=head_state_to_update,
        goto="method_router_node"
    )

def method_router_node(state: HeadState) -> Command[Literal["get_pruned_schema_from_rag", "get_pruned_schema_from_full_approach"]]:
    goto_node = "get_pruned_schema_from_rag" if state.get("rout_schema_through_rag") else "get_pruned_schema_from_full_approach"
    return Command(
        goto=goto_node
    )

def get_pruned_schema_from_rag(state: HeadState) -> Command[Literal["__end__"]]:
    """
    RAG node was used to find similar queries and this node will be used to get the pruned schema from those queries.
    """
    head_state_to_update = {
        "pruned_schema": json.dumps(
            get_pruned_schema(
                similar_data_queries=state.get("similar_data_query"),
                    from_rag=True
            ),
            indent=2
        ),
        "rout_schema_through_rag": True,
    }

    return Command(
        update=head_state_to_update,
        goto="__end__"
    )

def get_pruned_schema_from_full_approach(state: HeadState) -> Command[Literal["__end__"]]:
    head_state_to_update = {"pruned_schema": get_pruned_schema(
        similar_data_queries=None,
        from_rag=False
    )}
    return Command(
        update=head_state_to_update,
        goto="__end__"
    )



#===========================================================================
#                            BODY NODES
#===========================================================================

body_state_to_update = {
    # "dense_schema": {"table1": "col1, col2", "table2" : "col1, col4"},
    # "hints" : {"element": "table1.col1", "condition": "table1.col2 > 10", "keywords": "Group By"},
    # "gen_sql1": "gen_sql1",
    # "res_sql1": "res_sql1",
    # "gen_sql2": "gen_sql2",
    # "res_sql2": "res_sql2",
    # "gen_sql3": "gen_sql3",
    # "res_sql3": "res_sql3",
    # "final_answer": "final_answer",
}
def gen_sql1(state: BodyState) -> Command[Literal["get_schema_from_sql", "gen_sql3"]]:
    print("inside body")
    from utils import get_full_schema
    full_schema_json = get_full_schema()
    pruned_schema_json = state.get("pruned_schema")
    dummy_other_info = """The provided schema is in the following format:
    {
        'table_name': {
            'column_name_1' : 'datatype OR comma-separated enumerated values',
            'column_name_2' : 'datatype OR comma-separated enumerated values',
            ...
        },
        ...
    }"""
    # Dummy instructions for the SQL generation for now empty, add accordingly.
    dummy_instructions = """
    """
    sql1_output = generate_sql1(
        full_schema=json.dumps(full_schema_json, indent=2),
        pruned_schema=json.dumps(pruned_schema_json, indent=2),
        user_question=HumanMessage(state.get("data_query")),
        other_info=dummy_other_info,
        instructions=dummy_instructions,
    )

    body_state_to_update = {"gen_sql1": sql1_output}
    return Command(
        update=body_state_to_update,
        goto="get_schema_from_sql"
    )

def get_schema_from_sql(state: BodyState) -> Command[Literal["dense_schema"]]:
    sql = state.get("gen_sql1")
    table_column_map = extract_table_column_map(sql)
    body_state_to_update = {"extracted_schema_from_sql1": table_column_map}
    return Command(
        update=body_state_to_update,
        goto="dense_schema"
    )

def dense_schema(state: BodyState) -> Command[Literal["gen_hints"]]:
    pruned_schema = state.get("pruned_schema")
    extracted_schema_from_sql1 = state.get("extracted_schema_from_sql1")

    dense_schema = union_schemas(schema1_raw=pruned_schema, schema2_raw=extracted_schema_from_sql1)
    body_state_to_update = {"dense_schema": dense_schema}
    return Command(
        update=body_state_to_update,
        goto="gen_hints"
    )

def gen_hints(state: BodyState) -> Command[Literal["gen_sql2"]]:
    hints = generate_hints_for_sql2(
        dense_schema=state.get("dense_schema"),
        data_query=state.get("data_query"),
        other_info=""
    )
    body_state_to_update = {"hints": hints}
    return Command(
        update=body_state_to_update,
        goto="gen_sql2"
    )

def gen_sql2(state: BodyState) -> Command[Literal["execute_2sql"]]:
    sql2_output = generate_sql2(
        dense_schema=state.get("dense_schema"),
        hints=state.get("hints"),
        user_question=HumanMessage(content=state.get("data_query")),
        other_info=""
    )
    body_state_to_update = {"gen_sql2": sql2_output}
    return Command(
        update=body_state_to_update,
        goto="execute_2sql"
    )

def get_result_from_both_queries(state: BodyState) -> Command[Literal["gen_sql3"]]:
    # TODO : get result of both quries here
    res_sql1 = execute_sql_query(sql_query=state.get("gen_sql1"))["result"]
    res_sql2 = execute_sql_query(sql_query=state.get("gen_sql2"))["result"]
    body_state_to_update["res_sql1"] = res_sql1
    body_state_to_update["res_sql2"] = res_sql2
    return Command(
        update=body_state_to_update,
        goto="gen_sql3"
    )

def gen_sql3(state: BodyState) -> Command[Literal["loop_sql"]]:

    sql3_output = generate_sql3(
        sql1 = state.get("gen_sql1"),
        sql2 = state.get("gen_sql2"),
        res_sql1 = state.get("res_sql1"),
        res_sql2 = state.get("res_sql2"),
        dense_schema = state.get("dense_schema"),
        hints = state.get("hints"),
        user_question = HumanMessage(content=state.get("data_query"))
        )
    body_state_to_update = {"gen_sql3": sql3_output}
    return Command(
        update=body_state_to_update,
        goto="loop_sql"
    )

##########################################################################################
##########################LOOP THIS FUCKING NODE INSTEAD ################################
##########################################################################################
def loop_sql(state: BodyState) -> Command[Literal["loop_sql", "final_answer"]]:
    # TODO : extract sql history here
    sql_conv_hist = None

    max_retires_remaining = int(state.get("max_retires_remaining"))
    body_state_to_update["max_retires_remaining"] = max_retires_remaining - 1 if max_retires_remaining > 0 else 0

    ans_sql3 = execute_sql_query(sql_query=state.get("gen_sql3"))["result"]

    if ans_sql3 is None:
        goto_node = "loop_sql"
        loop_sql_output = loop_sql3(
            sql3=state.get("gen_sql3"),
            res_sql3=state.get("res_sql3"),
            dense_schema=state.get("dense_schema"),
            hints=state.get("hints"),
            user_question=HumanMessage(content=state.get("data_query")),
            sql_conversation_history=sql_conv_hist,
            max_retries=max_retires_remaining
        )
    else:
        goto_node = "final_answer"
    return Command(
        update=body_state_to_update,
        goto=goto_node
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
