# app/workflows/nodes/email_agent_node.py

from langchain_core.messages import AIMessage
from app.services.llm_service import llm_service

from app.prompts.agent_prompts import EMAIL_AGENT_PROMPT

def email_agent_node(state):
    messages = state["messages"]
    user_request = messages[-1].content

    # Format conversation history
    history_lines = []
    for msg in messages[:-1]:
        role = "User" if msg.type == "human" else "Assistant"
        history_lines.append(f"{role}: {msg.content}")
    conversation_history = "\n".join(history_lines)

    prompt = f"""{EMAIL_AGENT_PROMPT}

    Recent Conversation History:
    {conversation_history}

    User Request:
    "{user_request}"
    """

    draft = llm_service.chat(prompt)

    response_content = (
        f"✉️ **Email Agent: Draft Generated & Awaiting Approval**\n\n"
        f"{draft}\n\n"
        f"*Note: This action requires human-in-the-loop approval. Please reply with 'approve' to send or 'cancel' to discard.*"
    )

    return {
        "messages": [
            AIMessage(content=response_content)
        ],
        "requires_approval": True,
        "approved": False
    }