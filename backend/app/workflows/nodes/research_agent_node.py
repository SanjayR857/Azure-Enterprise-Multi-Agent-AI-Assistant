# app/workflows/nodes/research_agent_node.py

from langchain_core.messages import AIMessage

from app.services.agent_service import agent_service


def research_agent_node(state):

    messages = state["messages"]
    question = messages[-1].content

    # Format conversation history
    history_lines = []
    for msg in messages[:-1]:
        role = "User" if msg.type == "human" else "Assistant"
        history_lines.append(f"{role}: {msg.content}")
    conversation_history = "\n".join(history_lines)

    prompt = f"""Recent Conversation History:
{conversation_history}

Latest Request:
{question}
"""

    answer = agent_service.run(prompt)

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }