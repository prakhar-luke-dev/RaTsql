# -*- coding: utf-8 -*-
# File    : sql_tools.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/30/25 1:34 PM

from typing import Optional

from pydantic import BaseModel, Field


class SQLGenerator(BaseModel):
    """Generate SQL query based on a question, provided schema and instructions."""
    sql: str = Field(description="SQL query that answers the user question")
    invalid: Optional[bool] = Field(default=False, description="Indicates if the SQL query is generate or not, is not mark it 'True'")


class SQLHints(BaseModel):
    """Generate hints for the SQL2 query based on the question and provided schema."""
    elements: list[str] = Field(description="A list of tables and columns likely needed in the SQL query")
    conditions: list[str] = Field(description="Possible conditions and constraints for the WHERE clause, through decomposition and analysis of the question")
    keywords: list[str] = Field(description="SQL keywords (e.g., DISTINCT, GROUP BY) that may be relevant, by locating key indicator words in the question.")


