# -*- coding: utf-8 -*-
# File    : sql3.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 11:46 PM

from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from modules.custom_tools.sql_tools import SQLGenerator
from modules.prompts.sql3_prompts import SYSTEM_PROMPT_SQL3


def generate_structured_sql(
        llm_client: ChatOpenAI,
        sql1: str,
        sql2: str,
        res_sql1: str,
        res_sql2: str,
        dense_schema: str|dict,
        hints: str|dict,
        user_question: HumanMessage,
        instructions: str,
        other_info: str,
        examples: str
) -> dict[str, bool]:
    sys_message_content = SYSTEM_PROMPT_SQL3.format(
        sql1=sql1, sql2=sql2, res_sql1=res_sql1, res_sql2=res_sql2,
        dense_schema=dense_schema, hints=hints, query=user_question.content,
        instruction=instructions, other_info=other_info, examples=examples
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


def generate_sql3(
        sql1: str,
        sql2: str,
        res_sql1: dict,
        res_sql2: dict,
        dense_schema: str|dict,
        hints: str|dict,
        user_question: HumanMessage,
        instructions: str,
        other_info: str,
        examples: str
):
    """
    Generate SQL3 based SQL1, SQL2, their results, schema, user question, and other relevant information.
    :return:
    """
    llm_client = get_chat_model()
    if llm_client is not None:
        if res_sql1["error"] is None:
            res_sql1 = res_sql1["result"]
        if res_sql2["error"] is None:
            res_sql2 = res_sql2["result"]
        sql_validity = generate_structured_sql(
            llm_client=llm_client,
            sql1=sql1,
            sql2=sql2,
            res_sql1=res_sql1,
            res_sql2=res_sql2,
            dense_schema=dense_schema,
            hints=hints,
            user_question=user_question,
            instructions=instructions,
            other_info=other_info,
            examples=examples
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
