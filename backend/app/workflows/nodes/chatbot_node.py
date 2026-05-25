from langchain_core.messages import AIMessage

from app.services.llm_service import llm_service


def chatbot_node(state):

    messages = state["messages"]

    last_message = messages[-1]

    response = llm_service.chat(last_message.content)

    return {
        "messages": [
            AIMessage(content=response)
        ]
    }