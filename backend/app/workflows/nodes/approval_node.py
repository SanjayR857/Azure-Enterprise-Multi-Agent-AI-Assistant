from langgraph.types import interrupt

def approval_node(state):

    approval = interrupt(
        {
            "message": "Do you approve this acion?"
        }
    )


    return {
        "approved": approval
    }