# app/workflows/nodes/sql_agent_node.py

from langchain_core.messages import AIMessage
from app.services.sql_agent_service import sql_agent_service


def sql_agent_node(state):

    question = state["messages"][-1].content

    result = sql_agent_service.sql_agent.invoke(
        {
            "input": question
        }
    )

    return {
        "sql_result": result["output"]
    }