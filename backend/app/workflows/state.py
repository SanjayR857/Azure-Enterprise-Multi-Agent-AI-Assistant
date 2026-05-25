from typing import TypedDict
from typing import Annotated

from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    messages: Annotated[list, add_messages]