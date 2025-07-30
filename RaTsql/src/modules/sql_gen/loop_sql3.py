# -*- coding: utf-8 -*-
# File    : loop_sql3.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 7:03 PM

from modules.prompts.loop_sql3_prompt import LOOP_SQL3_SYS_PROMPT_1, LOOP_SQL3_SYS_PROMPT_2
from langchain_core.messages import HumanMessage, SystemMessage
from config import get_chat_model
from modules.custom_tools.sql_tools import SQLGenerator


def loop_sql3(
    sql3: str,
    res_sql3: str,
    dense_schema: str|dict,
    hints: str|dict,
    user_question: HumanMessage,
    sql_conversation_history: str = None,
    max_retries: int = 3,
):
    """
    Generate a new SQL query based on the provided SQL and error.

    Args:
        sql3 (str): The latest SQL query that resulted in an error.
        res_sql3 (str): The error message from the SQL execution.
        dense_schema (str): A dense representation of the schema.
        hints (str): Hints for generating the SQL query.
        query (str): The user question.
        sql_conversation_history (str, optional): Previous SQL queries and their results.

    Returns:
        str: The generated SQL query.
    """
    llm_client = get_chat_model()
    # for i in range(max_retries):
    if sql_conversation_history:
        # Use the second system prompt if conversation history is provided
        sys_message_content = LOOP_SQL3_SYS_PROMPT_2.format(
            sql3=sql3,
            res_sql3=res_sql3,
            sql_conversation_history=sql_conversation_history,
            dense_schema=dense_schema,
            hints=hints,
            query=user_question
        )
    else:
        # Use the first system prompt if no conversation history is provided
        sys_message_content = LOOP_SQL3_SYS_PROMPT_1.format(
            sql3=sql3,
            res_sql3=res_sql3,
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