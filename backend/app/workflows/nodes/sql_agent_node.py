# app/workflows/nodes/sql_agent_node.py

from langchain_core.messages import AIMessage


def sql_agent_node(state):

    return {
        "messages": [
            AIMessage(
                content="SQL Agent not implemented yet."
            )
        ]
    }