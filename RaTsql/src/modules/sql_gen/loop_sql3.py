# -*- coding: utf-8 -*-
# File    : loop_sql3.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 7:03 PM

from config import get_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from modules.custom_tools.sql_tools import SQLGenerator
from modules.prompts.loop_sql3_prompt import LOOP_SQL3_SYS_PROMPT_2


def loop_sql3(
    llm_client: ChatOpenAI,
    sql3: str,
    res_sql3: str,
    dense_schema: str|dict,
    hints: str|dict,
    user_question: HumanMessage,
    sql_conversation_history: list,
):
    """
    Generate a new SQL query based on the provided SQL and error.

    Args:
        sql3 (str): The latest SQL query that resulted in an error.
        res_sql3 (str): The error message from the SQL execution.
        dense_schema (str): A dense representation of the schema.
        hints (str): Hints for generating the SQL query.
        query (str): The user question.
        max_retries (int): Number of retires remaining in loop
        sql_conversation_history (str, optional): Previous SQL queries and their results.

    Returns:
        str: The generated SQL query.
    """

    sys_message_content = LOOP_SQL3_SYS_PROMPT_2.format(
        sql3=sql3,
        res_sql3=res_sql3,
        sql_conversation_history=sql_conversation_history,
        dense_schema=dense_schema,
        hints=hints,
        query=user_question
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

def loop_sql3_on_remaining_tries(
        sql_to_modify: str,
        res_sql3: str,
        dense_schema: str | dict,
        hints: str | dict,
        user_question: HumanMessage,
        max_retries: int,
        sql_conversation_history: list,
):
    llm_client = get_chat_model()
    if llm_client is not None:
        sql_validity = loop_sql3(
            llm_client=llm_client, sql3=sql_to_modify, res_sql3=res_sql3, dense_schema=dense_schema, hints=hints, user_question=user_question,
            sql_conversation_history=sql_conversation_history
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

