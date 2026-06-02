from app.core import config
from openai.types.responses import response
from langchain_core.messages import HumanMessage

from app.workflows.graph_builder import graph
import uuid

class WorkflowService:

    def run(self, message: str):
        

        response = graph.invoke(
        {
            "messages": [HumanMessage(content=message)]
        }
        )
        
        if response.get("final_response"):
            return response["final_response"]
        elif response.get("sql_result"):
            return response["sql_result"]
        elif response.get("rag_result"):
            return response["rag_result"]
        elif response.get("research_result"):
            return response["research_result"]
        
        return response["messages"][-1].content

workflow_service = WorkflowService()