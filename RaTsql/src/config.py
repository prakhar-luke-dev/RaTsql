# -*- coding: utf-8 -*-
# File    : config.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 11:32 PM
import os

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI, OpenAI

from google.cloud import bigquery
from google.oauth2 import service_account

from logs_operations.logger_setup import setup_logger

load_dotenv(find_dotenv(), override=True)
LANGFUSE_SECRET_KEY = str(os.getenv("LANGFUSE_SECRET_KEY"))
LANGFUSE_PUBLIC_KEY = str(os.getenv("LANGFUSE_PUBLIC_KEY"))
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
DEEPINFRA_API_TOKEN = str(os.getenv("DEEPINFRA_API_TOKEN"))
DEEPINFRA_BASE_URL = str(os.getenv("DEEPINFRA_BASE_URL"))

BQ_DATASET = os.getenv("BQ_DATASET")
BQ_GCP_PROJECT_ID = os.getenv("BQ_GCP_PROJECT_ID")
BQ_ACCOUNT_TYPE = os.getenv("BQ_ACCOUNT_TYPE")
BQ_PRIVATE_KEY_ID = os.getenv("BQ_PRIVATE_KEY_ID")
BQ_PRIVATE_KEY = os.getenv("BQ_PRIVATE_KEY")
BQ_CLIENT_EMAIL = os.getenv("BQ_CLIENT_EMAIL")
BQ_CLIENT_ID = os.getenv("BQ_CLIENT_ID")
BQ_AUTH_URI = os.getenv("BQ_AUTH_URI")
BQ_TOKEN_URI = os.getenv("BQ_TOKEN_URI")
BQ_AUTH_PROVIDER_X509_CERT_URL = os.getenv("BQ_AUTH_PROVIDER_X509_CERT_URL")
BQ_CLIENT_X509_CERT_URL = os.getenv("BQ_CLIENT_X509_CERT_URL")
BQ_UNIVERSAL_DOMAIN = os.getenv("BQ_UNIVERSAL_DOMAIN")

credentials_info = {
        "type": BQ_ACCOUNT_TYPE,
        "project_id": BQ_GCP_PROJECT_ID,
        "private_key_id": BQ_PRIVATE_KEY_ID,
        "private_key": BQ_PRIVATE_KEY,
        "client_email": BQ_CLIENT_EMAIL,
        "client_id": BQ_CLIENT_ID,
        "auth_uri": BQ_AUTH_URI,
        "token_uri": BQ_TOKEN_URI,
        "auth_provider_x509_cert_url": BQ_AUTH_PROVIDER_X509_CERT_URL,
        "client_x509_cert_url": BQ_CLIENT_X509_CERT_URL,
    }
credentials = service_account.Credentials.from_service_account_info(credentials_info)
BQ_CLIENT = bigquery.Client(credentials=credentials, project=BQ_GCP_PROJECT_ID)

graph_logger = setup_logger(log_file="logs/graph_logs.log", log_handler='graph_logger', backup=5)

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

dummy_other_info = """
    ## SCHEMA SAMPLE FORMAT : 
    {{
        'table_name': {{
            'column_name_1' : 'datatype OR comma-separated enumerated values',
            'column_name_2' : 'datatype OR comma-separated enumerated values',
            ...
        }},
        ...
    }}
    ## SCHEMA EXPLANATION :
    - Keys in the top-level dictionary are table names.
    - Inside each table, each column name maps to either:
        - a standard datatype like INT64, STRING, FLOAT64, DATE
        - or a string of comma-separated values (representing an ENUM type)
    - For each level in the hierarchy, there are two types of tables: those containing `_details` and `_performance` in the table name.
        - 1. The `_details` tables store metadata specific to that level, such as the 'entity's ID', 'name', 'status', 'type', and other relevant configuration or identification attributes. \
        This metadata is present only and exclusively in the `_details` tables (nowhere else in the database). \
        To retrieve or filter metadata, joins must be made using the relevant entity IDs.
            - Example, if you want to apply a WHERE clause on a campaign name, you should join using the `campaign_id` and then apply the condition on the `campaign_name` column from the table `google_ads_campaign_details_2643649617`.
        - 2. The `_performance` tables, contain day-wise performance metrics that are specific to the corresponding entity or level in the hierarchy. \
        These include metrics like 'clicks', 'impressions', 'conversions', and other quantitative indicators.
            - Example: If you want to fetch clicks at placements then it will be available in table `google_ads_placement_performance_2643649617` in column `metrics_clicks`, metrics specific to keywords will be in table `google_ads_keyword_performance_2643649617`.
    - Performance at any given level is typically evaluated using two key metrics: 
        - 1. The number of conversions (where a higher value is better) 
        - 2. the cost-per-click (CPC), where a lower value is preferred.
    
    # Before creation of query always below prefix and suffix to the table    
    TABLE_PREFIX = "data-pipeline.dataset.google_ads_"
    TABLE_SUFFIX = "_649617"
    
    # Query Optimization :
        - ALWAYS include condition ```sql WHERE customer_id = {customer_id}``` in the SQL Query (`customer_id` is present in every table. Do not use any join for this condition specifically.)
        - Always user SAFE_DIVIDE when dividing.
        - Use ORDER BY for sorted results
        - Use GROUP BY properly with non-aggregated columns
        - Use HAVING instead of WHERE for filtering aggregated results.
        - Use JOIN condition IF AND WHEN ABSOLUTELY NECESSARY as per question.
        - ALWAYS use INNER JOIN, LEFT JOIN, etc. appropriately based on relationships where needed.
        - Ensure JOIN conditions match valid foreign keys (e.g., ON table1.id = table2.table1_id).
        - Use IS NULL or IS NOT NULL for checking NULL values if the data type is STRING.
        - Use !=0 for checking non-zero values if the data type is INT64 whenever necessary.
        - Always validate aggregations work with the right columns (never SUM/AVG IDs)
        - ALWAYS use *`SAFE_DIVIDE(numerator, denominator)`* EVERYWHERE instead of direct division (e.g., `/`) to prevent divide-by-zero errors.

"""


