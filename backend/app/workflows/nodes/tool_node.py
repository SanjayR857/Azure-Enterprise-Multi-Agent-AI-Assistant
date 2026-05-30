from botocore import response
from langchain_core.messages import AIMessage

from app.services.agent_service import agent_service



def tool_node(state):

    question = state["messages"][-1].content

    response = agent_service.run(question)

    return{
        "messages": [
            AIMessage(content=response)
        ]
    }