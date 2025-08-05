# -*- coding: utf-8 -*-
# Project : 
# File    : utils.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM
import json
from collections import defaultdict
import warnings
from config import BQ_CLIENT
from google.api_core.exceptions import GoogleAPIError

def save_graph_to_file(runnable_graph, output_file_path):
    file_path = f"graph_visuals/{output_file_path}.png"
    png_bytes = runnable_graph.get_graph().draw_mermaid_png()
    with open(file_path, 'wb') as file:
        file.write(png_bytes)


def extract_union_table_column_map(similar_data_query) -> json:
    global_map = defaultdict(set)
    for item in similar_data_query.values():
        metadata_path = item.get("metadata_path")
        if not metadata_path:
            continue
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                table_column_map = data.get("table_column_map", {})
                for table, columns in table_column_map.items():
                    global_map[table].update(columns)
        except Exception as e:
            print(f"Error reading {metadata_path}: {e}")
    return_map = {table: sorted(columns) for table, columns in global_map.items()}
    return return_map

def get_pruned_schema(similar_data_queries, from_rag = False) -> dict[str: list[str]]:
    """
    Extract and union the schema from the metadata of similar data queries.
    :param from_rag:
    :param similar_data_queries:
    :return:
    """
    if from_rag or (similar_data_queries is None):
        return extract_union_table_column_map(similar_data_query=similar_data_queries)
    else:
        raise NotImplementedError("Pruned schema extraction from non-RAG, is not implemented yet.")
        # return None

def get_full_schema(path_of_schema: str = "/home/prakhar/luke-dev/txt2sql_methods/RaTsql/data/bq_metadata.json") -> json:
    try:
        with open(path_of_schema, 'r', encoding='utf-8') as f:
            full_schema = json.load(f)
        return full_schema
    except Exception as e:
        raise ValueError(f"Error while reading schema file {path_of_schema}")


def format_few_shots(few_shots, with_instructions=False) -> str:
    formatted = []
    for i, shot in enumerate(few_shots, 1):
        example = f"""### Example {i}:
Query: {shot['query']}
SQL: {shot['sql']}"""
        if with_instructions:
            example += f"\nInstruction: {shot['instructions'] or 'N/A'}"
        formatted.append(example)
    return "\n\n".join(formatted)


def format_query_specific_instructions(few_shots) -> str:
    formatted = []
    for i, shot in enumerate(few_shots, 1):
            if isinstance(shot['instructions'], str):
                instruction = f"""### Query Specific Instructions:
                        Instruction: {shot['instructions'] or 'N/A'}"""
                formatted.append(instruction)
    return "\n\n".join(formatted)



def create_dynamic_prompt(similar_data_query, want_few_shots = False, want_instructions = False) -> str | None:
    few_shots = []
    for item in similar_data_query.values():
        metadata_path = item.get("metadata_path")
        if not metadata_path:
            continue
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                instructions = data.get("instructions")
                if isinstance(instructions, str) and instructions.strip().lower() == "nan":
                    instructions = None

                few_shots.append({
                    "query": data.get("query", "").strip(),
                    "sql": data.get("sql", "").strip(),
                    "instructions": instructions.strip() if isinstance(instructions, str) else None
                })

        except Exception as e:
            print(f"Error reading {metadata_path}: {e}")
    if want_few_shots and not want_instructions:
        example_few_shots = format_few_shots(few_shots)
        return example_few_shots
    elif not want_few_shots and want_instructions:
        query_specific_inst = format_query_specific_instructions(few_shots)
        return query_specific_inst
    elif want_few_shots and want_instructions:
        warnings.warn(message="Dont try to mess around man, why do you want want both values at same time, you crazy ?",
                      category=UserWarning)
    return None


def union_schemas(schema1_raw, schema2_raw):
    # If inputs are JSON strings, parse them
    if isinstance(schema1_raw, str):
        schema1 = json.loads(schema1_raw)
    else:
        schema1 = schema1_raw

    if isinstance(schema2_raw, str):
        schema2 = json.loads(schema2_raw)
    else:
        schema2 = schema2_raw

    merged_schema = {}
    all_tables = set(schema1) | set(schema2)

    for table in all_tables:
        columns1 = set(schema1.get(table, []))
        columns2 = set(schema2.get(table, []))
        merged_schema[table] = sorted(columns1 | columns2)

    return merged_schema


def execute_sql_query(sql_query: str) -> dict[str, str|None]:
    """
    Execute the given SQL query and return the result.
    :param sql_query:
    :return:
    """
    client = BQ_CLIENT
    try:
        query_job = client.query(sql_query)
        results = query_job.result()
        rows = [dict(row) for row in results]
        return {
            "sql_query": sql_query,
            "result": rows if rows else None,
            "error": None
        }
    except GoogleAPIError as e:
        warnings.warn(
            "BigQuery API error during query execution.",
            UserWarning,
            stacklevel=2
        )
        return {
            "sql_query": sql_query,
            "result": None,
            "error": str(e)
        }
    except Exception as e:
        warnings.warn(
            "Unexpected error during SQL execution.",
            UserWarning,
            stacklevel=2
        )
        return {
            "sql_query": sql_query,
            "result": None,
            "error": str(e)
        }

