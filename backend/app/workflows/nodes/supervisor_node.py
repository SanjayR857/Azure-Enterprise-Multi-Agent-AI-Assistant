from app.services.llm_service import llm_service
from app.prompts.agent_prompts import SUPERVISOR_PROMPT
from langchain.messages import AIMessage

def supervisor_node(state):

    messages = state["messages"]
    user_message = messages[-1].content
    
    # Format conversation history
    history_lines = []
    for msg in messages[:-1]:
        role = "User" if msg.type == "human" else "Assistant"
        history_lines.append(f"{role}: {msg.content}")
    conversation_history = "\n".join(history_lines)

    prompt = f"""
    {SUPERVISOR_PROMPT}

    Recent Conversation History:
    {conversation_history}

    Latest User Request:
    {user_message}
    """

    response = llm_service.chat(prompt)
    next_agent = response.strip()

    return {
        "next_agent": next_agent
    }   