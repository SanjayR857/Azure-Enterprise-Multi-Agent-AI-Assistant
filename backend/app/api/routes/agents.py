# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.models.request_models import AgentRequest
from app.models.response_models import AgentResponse
from app.services.agent_service import agent_service
from app.utils import count_tokens

import asyncio

router = APIRouter(
    prefix="/api",
    tags=["agents"],
)


@router.post("/agent", response_model=AgentResponse)
async def agent(request: AgentRequest):

    # Run the blocking agent in a thread pool so the main event loop
    # stays free for MCP async I/O (tools use run_coroutine_threadsafe)
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, agent_service.run, request.message)
    
    input_tokens = count_tokens(request.message)
    output_tokens = count_tokens(response)
    
    return AgentResponse(
        input_token=input_tokens,
        output_token=output_tokens,
        total_token=input_tokens + output_tokens,
        response=response
    )

