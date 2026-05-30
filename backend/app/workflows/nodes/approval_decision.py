# app/workflows/nodes/approval_decision.py

def approval_decision(state):
    if state.get("approved"):
        return "send_email_node"
    return "end"
