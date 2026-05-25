from fastapi import APIRouter
from app.models.request_models import ChatRequest
from app.models.response_models import RequestModel
from app.services.llm_service import llm_service


router = APIRouter(
    prefix="/api",
    tags=["chat"],
)


@router.post("/chat", response_model=RequestModel)
async def chat(request: ChatRequest):

    response = llm_service.chat(request.message)

    return RequestModel(response=response)