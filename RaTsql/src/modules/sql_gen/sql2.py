# -*- coding: utf-8 -*-
# File    : sql2.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 11:45 PM

from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from modules.custom_tools.sql_tools import SQLGenerator
from modules.prompts.sql2_prompts import SYSTEM_PROMPT_SQL2


def generate_structured_sql2(llm_client: ChatOpenAI, dense_schema: str|dict, hints: dict, user_question: HumanMessage, other_info: str):
    """
    Generate SQL2 based on the dense schema, hints, user question, and other relevant information.
    :param llm_client: The LLM client to use for generating SQL2.
    :param dense_schema: The dense schema in string or dictionary format.
    :param hints: A dictionary containing hints for the SQL2 query.
    :param user_question: The user's question to be answered by the SQL2 query.
    :param other_info: Any other relevant information that might help in generating the SQL2
    :return: A dictionary containing the generated SQL2 query and its validity.
    """
    sys_message_content = SYSTEM_PROMPT_SQL2.format(
        query=user_question,
        dense_schema=dense_schema,
        hints=hints,
        other_info=other_info
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

def generate_sql2(dense_schema: str|dict, hints: dict, user_question: HumanMessage, other_info:str):
    """
    Generate SQL2 based on the dense schema, hints, user question, and other relevant information.
    :param: dense_schema: The dense schema in string or dictionary format.
    :param: hints: A dictionary containing hints for the SQL2 query.
    :param: user_question: The user's question to be answered by the SQL2 query.
    :param: other_info: Any other relevant information that might help in generating the SQL2
    :return:
    """
    llm_client = get_chat_model()
    if llm_client is not None:
        sql2_validity = generate_structured_sql2(
            llm_client=llm_client,
            dense_schema=dense_schema,
            hints=hints,
            user_question=user_question,
            other_info=other_info
        )
        if ("invalid" in sql2_validity) and ("sql" in sql2_validity):
            if isinstance(sql2_validity['invalid'], bool):
                if not sql2_validity["invalid"]:
                    sql2 = sql2_validity["sql"]
                    return sql2
            elif isinstance(sql2_validity['invalid'], str):  # incase LLM hallucinates and returns a string instead of bool.
                if (sql2_validity['invalid']).lower() == "false":
                    sql2 = sql2_validity["sql"]
                    return sql2
            else:
                raise ValueError(
                    "No sql found , it's invalid or not generated (question might not be related to the schema).")