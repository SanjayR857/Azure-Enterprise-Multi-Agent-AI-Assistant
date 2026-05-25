from fastapi import APIRouter

from app.models.request_models import ChatRequest
from app.models.response_models import RequestModel
from app.services.llm_service import llm_service
from app.utils import count_tokens

router = APIRouter(
    prefix="/api",
    tags=["chat"],
)


@router.post("/chat", response_model=RequestModel)
async def chat(request: ChatRequest):

    response = llm_service.chat(request.message)
    
    input_tokens = count_tokens(request.message)
    output_tokens = count_tokens(response)
    
    return RequestModel(
        input_token=input_tokens,
        output_token=output_tokens,
        total_token=input_tokens + output_tokens,
        response=response
    )
