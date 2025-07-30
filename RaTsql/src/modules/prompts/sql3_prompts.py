# -*- coding: utf-8 -*-
# File    : sql3_prompts.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 6:33 PM

SYSTEM_PROMPT_SQL3 = """
Your task is to generate a new SQL query for the user question, Take into account the provided SQL1 and SQL2 query.
You're provided with 
1. SQL1 query with it's execution result.
2. SQL2 query with it's execution result.
3. Dense schema, which is a dense representation of the schema.
4. Hints, which are some hints in order to generate the SQL query.
5. User question. 
Both SQL1 and SQL2 queries tries to answer the user question,
#### SQL1 Query: 
{sql1}

#### SQL1 Result: 
{res_sql1}

#### SQL2 Query: 
{sql2}

#### SQL2 Result: 
{res_sql2}

#### Dense Schema: 
{dense_schema}

#### Hints: 
here is what each hint means:
- condition list: all conditions extracted from the user question.
- elements list: a list of tables and columns likely needed in the SQL query.
- keywords list: SQL keywords that may be relevant to the user's question.

{hints}

#### User Question : 
{query}
"""

sq3_input_variables = ["sql1", "res_sql1", "sql2", "res_sql2", "dense_schema", "hints", "query"]
