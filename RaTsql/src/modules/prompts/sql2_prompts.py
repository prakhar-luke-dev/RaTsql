# -*- coding: utf-8 -*-
# File    : sql2_prompts.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 6:19 PM

SYSTEM_PROMPT_SQL2 = """
Answer the user query based on given schema :
Here is the dense schema of the database:
{dense_schema}.\n

Below are the hints in order to generate the SQL query:
{hints}\n
here is what each hint means:
- condition list: all conditions extracted from the user question.
- elements list: a list of tables and columns likely needed in the SQL query.
- keywords list: SQL keywords that may be relevant to the user's question.


{query}\n"

If the user query is not related to the schema, return 'None' as the sql query.
Here are some other information that you should consider while generating the sql query:
{other_info}\n

"""

sq2_input_variables = ["query", "dense_schema", "hints", "other_info"]
