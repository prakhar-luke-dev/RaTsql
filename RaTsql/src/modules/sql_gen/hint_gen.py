# -*- coding: utf-8 -*-
# File    : hint_gen.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 3:47 PM

from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from modules.custom_tools.sql_tools import SQLHints
from modules.prompts.hint_prompts import HINT_SYSTEM_PROMPT


def generate_hints(llm_client: ChatOpenAI, dense_schema: dict|str, data_query: str, other_info: str):
    try:
        sys_message_content = HINT_SYSTEM_PROMPT.format(
            data_query=data_query,
            dense_schema=dense_schema,
            other_info=other_info
        )
        sys_message = SystemMessage(content=sys_message_content)
        llm_with_tools = llm_client.bind_tools([SQLHints])
        user_message = HumanMessage(content=data_query)
        response = llm_with_tools.invoke([sys_message, user_message])
        # Parse output
        if hasattr(response, "tool_calls") and response.tool_calls:
            parsed = response.tool_calls[0]["args"]
        elif hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
            parsed = response.additional_kwargs["tool_calls"][0]["args"]
        else:
            raise ValueError(f"❌ No tool output found in response: {response}")
        return parsed
    except Exception as e:
        raise ValueError(f"Error while generating hints: {e}")

def generate_hints_for_sql2(dense_schema: dict|str, data_query: str, other_info: str):
    """
    Generate hints for SQL2 query based on the dense schema, user question, and other relevant information.
    :param dense_schema:
    :param data_query:
    :param other_info:
    :return:
    """
    llm_client = get_chat_model()
    augmented_hints = generate_hints(
        llm_client=llm_client,
        dense_schema=dense_schema,
        data_query=data_query,
        other_info=other_info,
    )
    if ("elements" in augmented_hints) and ("conditions" in augmented_hints) and ("keywords" in augmented_hints):
        return augmented_hints
    if llm_client is not None:
        pass
    else:
        raise ValueError("No LLM client available for generating hints.")