from openai.types.responses import response
from langchain_core.messages import HumanMessage

from app.workflows.graph_builder import graph

class WorkflowService:

    def run(self, message: str):

        response = graph.invoke(
        {
            "messages": [HumanMessage(content=message)]
        }
        )

        return response["messages"][-1].content

workflow_service = WorkflowService()