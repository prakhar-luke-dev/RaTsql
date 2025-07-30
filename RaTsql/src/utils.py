# -*- coding: utf-8 -*-
# Project : 
# File    : utils.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM
import json
from collections import defaultdict

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
    # # Convert to sorted lists
    # final_map = {table: sorted(columns) for table, columns in global_map.items()}
    #
    # # Return as JSON string (pretty-printed)
    # return json.dumps(final_map, indent=2)

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


import json

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

def execute_sql_query(sql_query: str):
    """
    Execute the given SQL query and return the result.
    :param sql_query:
    :return:
    """
    try:
        # TODO : execute the SQL query here
        sql_result = "this is a mock result for the SQL query"
        if len(sql_result) == 0:
            sql_result = None
    except Exception as e:
        sql_result = None
    return {
        "sql_query": sql_query,
        "result": sql_result,
        "error": None if sql_result is not None else str(e)
    }