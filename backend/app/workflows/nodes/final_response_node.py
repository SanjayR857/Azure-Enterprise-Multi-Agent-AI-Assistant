from langchain_core.messages import AIMessage

def final_response_node(state):

    return {
        "messages": [
            AIMessage(
                content=state["final_response"]
            )
        ]
    }