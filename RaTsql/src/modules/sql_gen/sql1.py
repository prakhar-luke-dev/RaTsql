# -*- coding: utf-8 -*-
# File    : sql1.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 11:45 PM


import json

from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from modules.custom_tools.sql_tools import SQLGenerator
from modules.prompts.sql1_prompts import SYSTEM_PROMPT_SQL1


def generate_structured_sql(llm_client: ChatOpenAI, full_schema: json, pruned_schema: json, user_question: HumanMessage, instructions: str, other_info: str) -> dict[str, bool]:
    sys_message_content = SYSTEM_PROMPT_SQL1.format(
        query = user_question.content,
        full_schema = json.dumps(full_schema, indent=2),
        pruned_schema = json.dumps(pruned_schema, indent=2),
        instruction = instructions,
        other_info = other_info
    )
    system_message = SystemMessage(content=sys_message_content)
    llm_with_tools = llm_client.bind_tools([SQLGenerator])

    response = llm_with_tools.invoke([system_message, user_question])

    # Parse output
    if hasattr(response, "tool_calls") and response.tool_calls:
        parsed = response.tool_calls[0]["args"]
    elif hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
        parsed = response.additional_kwargs["tool_calls"][0]["args"]
    else:
        raise ValueError(f"❌ No tool output found in response: {response}")
    return parsed


def generate_sql1(full_schema: json, pruned_schema: json, user_question: HumanMessage, other_info: str, instructions: str):
    """
    Generate SQL1 based on the full schema and pruned schema, user question, and other relevant information.
    :return:
    """
    # model_to_use = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
    # model_to_use = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    llm_client = get_chat_model()
    if llm_client is not None:
        sql_validity =  generate_structured_sql(
            llm_client=llm_client,
            full_schema=full_schema,
            pruned_schema=pruned_schema,
            user_question=user_question,
            instructions=instructions,
            other_info=other_info
        )
        if ("invalid" in sql_validity) and ("sql" in sql_validity):
            if isinstance(sql_validity['invalid'], bool):
                if not sql_validity["invalid"]:
                    sql1 = sql_validity["sql"]
                    return sql1
            elif isinstance(sql_validity['invalid'], str):  # incase LLM hallucinates and returns a string instead of bool.
                if (sql_validity['invalid']).lower() == "false":
                    sql1 = sql_validity["sql"]
                    return sql1
            else:
                raise ValueError("No sql found , it's invalid or not generated (question might not be related to the schema).")
