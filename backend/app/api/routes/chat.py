# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from app.services.agent_service import agent_service
from app.models.response_models import AgentResponse
from app.models.request_models import AgentRequest
from app.utils import count_tokens

import asyncio

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@router.post("/",response_model=AgentResponse)
async def chat(request:AgentRequest):
    
    # Run the blocking workflow in a thread pool so the main event loop
    # stays free for MCP async I/O (tools use run_coroutine_threadsafe)
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, agent_service.run_orchestrator, request.message)
    
    input_tokens = count_tokens(request.message)
    output_tokens = count_tokens(response)
    
    return AgentResponse(
        input_token=input_tokens,
        output_token=output_tokens,
        total_token=input_tokens + output_tokens,
        response=response
    )

