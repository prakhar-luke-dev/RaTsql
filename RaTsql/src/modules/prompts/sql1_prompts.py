# -*- coding: utf-8 -*-
# File    : sql1_prompts.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 1:49 AM

SYSTEM_PROMPT_SQL1 = """
Answer the user query based on given schema :
Here is the full schema of the database:
{full_schema}.\n

Here is the schema that you should focus on to answer the user query:
{pruned_schema}.\n

{instruction}\n

{query}\n"

If the user query is not related to the schema, return 'None' as the sql query.
Here are some other information that you should consider while generating the sql query:
{other_info}\n

"""

sq1_input_variables = ["query", "full_schema", "pruned_schema", "instruction", "other_info"]


