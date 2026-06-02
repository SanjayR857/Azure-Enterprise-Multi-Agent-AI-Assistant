from typing import TypedDict
from typing import Annotated

from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    messages: Annotated[list, add_messages]
    next_agent: str 
    
    research_result: str
    rag_result: str
    sql_result: str

    final_response: str

    # email 
    
    # requires_approval: bool
    # approved: bool