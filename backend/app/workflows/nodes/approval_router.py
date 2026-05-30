# app/workflows/nodes/approval_router.py

def approval_router(state):
    if state.get("requires_approval"):
        return "approval_node"
    return "supervisor"