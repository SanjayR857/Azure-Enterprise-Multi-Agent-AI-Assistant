# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from app.services.workflow_service import workflow_service
from app.models.response_models import AgentResponse
from app.models.request_models import AgentRequest
from app.utils import count_tokens

router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
)


@router.post("/",response_model=AgentResponse)
async def run_workflow(request:AgentRequest):
    
    response = workflow_service.run(request.message)
    
    input_tokens = count_tokens(request.message)
    output_tokens = count_tokens(response)
    
    return AgentResponse(
        input_token=input_tokens,
        output_token=output_tokens,
        total_token=input_tokens + output_tokens,
        response=response
    )
