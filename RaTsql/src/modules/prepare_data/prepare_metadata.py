# -*- coding: utf-8 -*-
# File    : prepare_metadata.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/29/25 5:37 PM

#===========================================================================
#  *                                 INFO
#    This script takes csv and output json files for each query.
#    Each json is in below format :
#       {
#           "ref_id": "query_xxx",
#           "query": "",
#           "sql": "",
#           "tables": [],
#           "columns": [],
#           "brand_id": "12311231",
#           "brand_name": "brand name",
#           "category": "Campaign",
#           "instructions": "nan",
#           "instructions_comment": "nan"
#       }
#
#
#===========================================================================
import os
import pandas as pd
import sqlglot
from deprecated import deprecated
from sqlglot import parse_one
import json
from pathlib import Path
# TODO : Next time store respective columns in respective tables
# Customize these
CSV_PATH = "/home/prakhar/luke-dev/txt2sql_methods/RaTsql/notebooks/dummy_sql_ground_truth_for_automated_testing - Sheet1.csv"
BASE_OUTPUT_DIR = "/home/prakhar/luke-dev/txt2sql_methods/RaTsql/data/metadata_query_store/"
REGISTRY_FILE = "/home/prakhar/luke-dev/txt2sql_methods/RaTsql/data/lookup_query_registry.json"
TABLE_PREFIX = "google_ads_"
TABLE_SUFFIX = "_2643649617"
SHARD_SIZE = 10  # Size for sharding

# Ensure base output directory exists
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

def clean_table_name(name):
    if name.startswith(TABLE_PREFIX):
        name = name[len(TABLE_PREFIX):]
    if name.endswith(TABLE_SUFFIX):
        name = name[: -len(TABLE_SUFFIX)]
    return name

@deprecated(reason="this version used to store table and column names separately, now we store them in a mapping")
def extract_tables_and_columns_flat(sql):
    try:
        expression = parse_one(sql, read='bigquery')
        tables = {
            clean_table_name(table.name)
            for table in expression.find_all(sqlglot.exp.Table)
        }
        columns = {col.name for col in expression.find_all(sqlglot.exp.Column)}
        return list(tables), list(columns)
    except Exception as e:
        return [], []

def extract_table_column_map(sql):
    try:
        expression = parse_one(sql, read='bigquery')

        table_aliases = {}
        # Build table alias mapping
        for table_expr in expression.find_all(sqlglot.exp.Table):
            actual_name = clean_table_name(table_expr.name)
            alias = table_expr.alias_or_name
            table_aliases[alias] = actual_name

        table_column_map = {}

        for col in expression.find_all(sqlglot.exp.Column):
            if col.table:
                alias = col.table
                table = table_aliases.get(alias, alias)
                column_name = col.name
                table_column_map.setdefault(table, set()).add(column_name)
            else:
                # No table prefix in column
                for table in table_aliases.values():
                    table_column_map.setdefault(table, set()).add(col.name)

        # Convert sets to sorted lists for JSON serialization
        return {table: sorted(cols) for table, cols in table_column_map.items()}
    except Exception as e:
        return {}

if __name__ == "__main__":
    # Read CSV with automatic separator detection
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig', sep=None, engine='python')
    df.columns = df.columns.str.strip()

    registry = []
    shard_registry = {}
    for idx, row in df.iterrows():
        query = str(row.get('Questions', '')).strip()
        sql = str(row.get('Ground truth sql', '')).strip()

        if not query or not sql or sql.lower() == 'nan':
            continue

        table_column_map = extract_table_column_map(sql)
        tables = list(table_column_map.keys())
        columns = sorted(set(col for cols in table_column_map.values() for col in cols))

        ref_id = f"query_{idx:05}"  # 5-digit padding
        shard_id = idx // SHARD_SIZE
        shard_dir = os.path.join(BASE_OUTPUT_DIR, f"{shard_id:02d}")
        os.makedirs(shard_dir , exist_ok=True)

        file_path = os.path.join(shard_dir, f"{ref_id}.json")

        table_column_map = extract_table_column_map(sql)

        entry = {
            "ref_id": ref_id,
            "query": query,
            "sql": sql,
            "tables": list(table_column_map.keys()),
            "columns": sorted(set(col for cols in table_column_map.values() for col in cols)),
            "table_column_map": table_column_map,  # <-- added mapping
            "brand_id": str(int(row.get("Brand id", ""))).strip(),
            "brand_name": str(row.get("Brand Name", "")).strip(),
            "category": str(row.get("Category", "")).strip(),
            "instructions": str(row.get("Instructions", "")).strip(),
            "instructions_comment": str(row.get("Instructions comment", "")).strip(),
        }

        with open(file_path, "w") as f:
            json.dump(entry, f, indent=2)

        if shard_id not in shard_registry:
            shard_registry[shard_id] = []
        shard_registry[shard_id].append({
            "ref_id": ref_id,
            "file": file_path,
            "query": query
        })

    # Save master registry
    for shard_id, entries in shard_registry.items():
        shard_dir = os.path.join(BASE_OUTPUT_DIR, f"{shard_id:02d}")
        registry_path = os.path.join(shard_dir, "lookup_registry.json")
        with open(registry_path, "w") as f:
            json.dump(entries, f, indent=2)
        print(f"✅ Saved {len(registry)} queries in shards under {BASE_OUTPUT_DIR} and registry to {REGISTRY_FILE}")
