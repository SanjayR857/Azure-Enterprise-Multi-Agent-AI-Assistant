# app/workflows/nodes/approval_node.py

from langchain_core.messages import AIMessage

def approval_node(state):
    messages = state["messages"]
    user_message = messages[-1].content
    user_message_clean = user_message.strip().lower()
    
    if any(word in user_message_clean for word in ["approve", "yes", "confirm", "send"]):
        return {
            "requires_approval": False,
            "approved": True
        }
    elif any(word in user_message_clean for word in ["cancel", "no", "discard", "stop"]):
        return {
            "messages": [
                AIMessage(content="✉️ **Status: Draft Discarded.**\n\nThe email draft has been successfully cancelled and discarded.")
            ],
            "requires_approval": False,
            "approved": False
        }
    else:
        return {
            "messages": [
                AIMessage(content="⚠️ **Pending Approval:** You have a drafted email awaiting confirmation.\n\n*Please type 'approve' to send the email or 'cancel' to discard it before asking a new question.*")
            ],
            "requires_approval": True,
            "approved": False
        }