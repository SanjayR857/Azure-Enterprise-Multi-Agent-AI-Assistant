# app/workflows/nodes/chatbot_agent_node.py

from langchain_core.messages import AIMessage

from app.services.llm_service import llm_service


def chatbot_agent_node(state):

    question = state["messages"][-1].content

    answer = llm_service.chat(question)

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }