from langchain_core.messages import AIMessage
from app.services.agent_service import agent_service


def chatbot_agent_node(state):

    user_message = state["messages"][-1].content
    answer = agent_service.run(user_message)

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }