# -*- coding: utf-8 -*-
# File    : config.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 11:32 PM
from langchain_openai import ChatOpenAI, OpenAI
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)
LANGFUSE_SECRET_KEY = str(os.getenv("LANGFUSE_SECRET_KEY"))
LANGFUSE_PUBLIC_KEY = str(os.getenv("LANGFUSE_PUBLIC_KEY"))
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
DEEPINFRA_API_TOKEN = str(os.getenv("DEEPINFRA_API_TOKEN"))
DEEPINFRA_BASE_URL = str(os.getenv("DEEPINFRA_BASE_URL"))



def get_chat_model(model_name: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo", _temp: float = 0, _verbose: bool=False) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=DEEPINFRA_API_TOKEN,
        base_url=DEEPINFRA_BASE_URL,
        model=model_name,
        temperature= _temp,
        verbose=_verbose
    )

def get_llm_model(model_name: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo", _temp: float = 0) -> OpenAI:
    try:
        return OpenAI(
            api_key=DEEPINFRA_API_TOKEN,
            base_url=DEEPINFRA_BASE_URL,
            model=model_name,
            temperature= _temp
        )
    except Exception as e:
        return None


FULL_SCHEMA = """
"""