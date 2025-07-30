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
from sqlglot import parse_one
import json
from pathlib import Path

# Customize these
CSV_PATH = "/home/prakhar/luke-dev/txt2sql_methods/RaTsql/notebooks/dummy_sql_ground_truth_for_automated_testing - Sheet1.csv"
BASE_OUTPUT_DIR = "metadata_query_store/"
REGISTRY_FILE = "query_registry.json"
TABLE_PREFIX = "google_ads_"
TABLE_SUFFIX = "_2643649617"
SHARD_SIZE = 100

# Ensure base output directory exists
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

def clean_table_name(name):
    if name.startswith(TABLE_PREFIX):
        name = name[len(TABLE_PREFIX):]
    if name.endswith(TABLE_SUFFIX):
        name = name[: -len(TABLE_SUFFIX)]
    return name

def extract_tables_and_columns(sql):
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

# Read CSV with automatic separator detection
df = pd.read_csv(CSV_PATH, encoding='utf-8-sig', sep=None, engine='python')
df.columns = df.columns.str.strip()

registry = []

for idx, row in df.iterrows():
    query = str(row.get('Questions', '')).strip()
    sql = str(row.get('Ground truth sql', '')).strip()

    if not query or not sql or sql.lower() == 'nan':
        continue

    tables, columns = extract_tables_and_columns(sql)

    ref_id = f"query_{idx:05}"  # 5-digit padding
    shard_id = idx // SHARD_SIZE
    shard_dir = os.path.join(BASE_OUTPUT_DIR, f"{shard_id:02d}")
    os.makedirs(shard_dir, exist_ok=True)

    file_path = os.path.join(shard_dir, f"{ref_id}.json")

    entry = {
        "ref_id": ref_id,
        "query": query,
        "sql": sql,
        "tables": tables,
        "columns": columns,
        "brand_id": str(int(row.get("Brand id", ""))).strip(),
        "brand_name": str(row.get("Brand Name", "")).strip(),
        "category": str(row.get("Category", "")).strip(),
        "instructions": str(row.get("Instructions", "")).strip(),
        "instructions_comment": str(row.get("Instructions comment", "")).strip(),
    }

    with open(file_path, "w") as f:
        json.dump(entry, f, indent=2)

    registry.append({
        "ref_id": ref_id,
        "file": file_path,
        "query": query
    })

# Save master registry
with open(REGISTRY_FILE, "w") as f:
    json.dump(registry, f, indent=2)

print(f"✅ Saved {len(registry)} queries in shards under {BASE_OUTPUT_DIR} and registry to {REGISTRY_FILE}")
