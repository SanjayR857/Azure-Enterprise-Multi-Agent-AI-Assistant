# app/workflows/nodes/chatbot_agent_node.py

from langchain_core.messages import AIMessage

from app.services.llm_service import llm_service


def chatbot_agent_node(state):

    answer = llm_service.chat(state["messages"])

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }