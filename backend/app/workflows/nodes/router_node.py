
def router_node(state):

    message = state['messages'][-1].content

    if any (word in message.lower() for word in [
        "pdf",
        "document",
        "file",
        "uploaded",
        "according to"
    ]):
        route = "rag"
    
    elif any(word in message.lower() for word in[
        "search",
        "latest",
        "news",
        "current",
        "today"
    ]):
        route = "tool"

    else:
        route = "chatbot"
    
    return {
        "route": route
    }