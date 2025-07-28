# -*- coding: utf-8 -*-
# Project :
# File    : states.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM


from langgraph.graph import MessagesState, START
from typing import Optional
#===========================================================================
#                            GLOBAL STATE
#===========================================================================

class GlobalState(MessagesState):
    data_query : str
    sub_graph_selected : str
    similar_data_query : dict
    similarity_threshold : float
    pruned_schema: dict
    final_answer: str


#===========================================================================
#                            HEAD STATE
#===========================================================================
class HeadState(GlobalState):
    # similar_data_query : dict
    # similarity_threshold : float
    
    rout_schema_through_rag : bool
    # pruned_schema : dict


#===========================================================================
#                            BODY STATE
#===========================================================================
    
class BodyState(HeadState):
    dense_schema : dict
    hints : dict
    gen_sql1 : str
    res_sql1 : str

    gen_sql2 : str
    res_sql2 : str
    
    gen_sql3 : str
    res_sql3 : str

    # final_answer : str

#===========================================================================
#                            TAIL STATE
#===========================================================================

class TailState(BodyState):
    need_feedback : bool
    feedback_category : bool # true = positive, false = negative
    feedback_message : str
    

