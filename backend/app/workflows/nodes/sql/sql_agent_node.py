# app/workflows/nodes/sql_agent_node.py

from langchain_core.messages import AIMessage
from app.services.agent_service import agent_service


def sql_agent_node(state):

    question = state["messages"][-1].content

    result = agent_service.run_sql_agent(question)

    return {
        "sql_result": result
    }