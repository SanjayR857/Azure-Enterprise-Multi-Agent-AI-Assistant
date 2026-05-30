from app.core import config
from openai.types.responses import response
from langchain_core.messages import HumanMessage

from app.workflows.graph_builder import graph
import uuid

class WorkflowService:

    def run(self, message: str):
        
        thread_id = "user_123"

        response = graph.invoke(
        {
            "messages": [HumanMessage(content=message)]
        },
        config={"configurable": 
            {"thread_id": thread_id}}   
        )

        return response["messages"][-1].content

workflow_service = WorkflowService()