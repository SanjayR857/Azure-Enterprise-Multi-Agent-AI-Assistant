# app/workflows/nodes/email_agent_node.py

from langchain_core.messages import AIMessage
from app.services.llm_service import llm_service

from app.prompts.agent_prompts import EMAIL_AGENT_PROMPT

def email_agent_node(state):
    user_request = state["messages"][-1].content

    prompt = f"""{EMAIL_AGENT_PROMPT}

    User Request:
    "{user_request}"
    """

    draft = llm_service.chat(prompt)

    response_content = (
        f"✉️ **Email Agent: Draft Generated**\n\n"
        f"{draft}"
    )

    return {
        "final_response": response_content
    }