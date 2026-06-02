# app/workflows/nodes/send_email_node.py

from langchain_core.messages import AIMessage

def send_email_node(state):
    # In a real-world enterprise app, you would integrate SMTP, AWS SES, or SendGrid here.
    # For the workflow demo, we simulate a successful transmission of the drafted email.
    
    return {
        "messages": [
            AIMessage(content="🚀 **Email Dispatched Successfully!**\n\nThe approved draft has been securely transmitted through the enterprise email server to the recipient.")
        ],
        "requires_approval": False,
        "approved": False  # Reset the state for the next session
    }
