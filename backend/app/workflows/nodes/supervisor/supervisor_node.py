from app.services.llm_service import llm_service
from app.prompts.agent_prompts import SUPERVISOR_PROMPT
from langchain.messages import AIMessage

def supervisor_node(state):

    user_message = state["messages"][-1].content
    
    prompt = f"""
    {SUPERVISOR_PROMPT}

    Latest User Request:
    {user_message}
    """

    response = llm_service.chat(prompt)
    next_agent = response.strip()

    return {
        "next_agent": next_agent
    }   