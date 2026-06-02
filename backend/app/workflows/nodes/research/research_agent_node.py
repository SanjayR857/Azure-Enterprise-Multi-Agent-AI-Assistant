# app/workflows/nodes/research_agent_node.py

from langchain_core.messages import AIMessage

from app.services.agent_service import agent_service


def research_agent_node(state):

    question = state["messages"][-1].content

    result = agent_service.run(question)

    return {
        "research_result": result
    }