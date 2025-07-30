from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
import json
from config import get_chat_model  # adjust import to match your setup


# 🔧 Define structured tool
class SQLGenerator(BaseModel):
    """Generate SQL query based on a question and provided schema"""
    sql: str = Field(description="SQL query that answers the user question")
    invalid: Optional[bool] = Field(default=False, description="Indicates if the SQL query is generate or not, is not mark it 'True'")


# 🧠 Main function
def sql1_gen(
        usr_message: HumanMessage,
        model_to_use: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        temperature: float = 0.3,
) -> dict:
    ps = {
        "table_column_map": {
            "campaign_details": [
                "campaign_id",
                "campaign_name",
                "total_impressions"
            ],
            "campaign_performance": [
                "campaign_id",
                "customer_id",
                "metrics_impressions",
                "segments_date",
                "total_impressions"
            ]
        }
    }

    other_info = """The provided schema is in the following format:
    {
        'table_name': {
            'column_name_1' : 'datatype OR comma-separated enumerated values',
            'column_name_2' : 'datatype OR comma-separated enumerated values',
            ...
        },
        ...
    }"""

    # 🧾 Prompt
    SQL_SYS_PROMPT = f"""
Answer the user query based on given schema:

Here is the schema that you should focus on to answer the user query:
{json.dumps(ps, indent=2)}

User Query:
{usr_message.content}

If the user query is not related to the schema, return 'None' as the SQL query.

Additional Info:
{other_info}
"""

    # 🔧 Create messages
    system_message = SystemMessage(content=SQL_SYS_PROMPT)

    # 🚀 Load model
    llm_client = get_chat_model(model_name=model_to_use, _temp=temperature, _verbose=True)
    llm_client = llm_client.bind_tools([SQLGenerator])  # 🔐 tool binding

    # 🧠 Inference
    response = llm_client.invoke([system_message, usr_message])

    # 🧼 Parse output
    if hasattr(response, "tool_calls") and response.tool_calls:
        parsed = response.tool_calls[0]["args"]
    elif hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
        parsed = response.additional_kwargs["tool_calls"][0]["args"]
    else:
        raise ValueError(f"❌ No tool output found in response: {response}")

    return parsed



from langchain_core.messages import HumanMessage

# user_msg = HumanMessage(content="Hi how are YOU?")
user_msg = HumanMessage(content="Which campaign had the maximum impressions on 1 jan 2025?")
response = sql1_gen(user_msg)
print(f"Response : {response}\n")
# print(response["sql"])
# print(response.get('invalid'), type(response.get('invalid')))
# print("invalid" in response)
if ("invalid" in response) and ("sql" in response):
    if not response["invalid"]:
        sql1 = response["sql"]
        print(f"sql1 : {sql1}")
    else:
        print("No sql found , it's invalid or not generated (question might not be related to the schema).")