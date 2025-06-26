from fastapi import APIRouter, Request
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import AgentService
from app.core.logging import get_logger

router = APIRouter()
agent_service = AgentService()
logger = get_logger(__name__)

@router.post("/api/reply", response_model=ChatResponse)
async def reply_to_message(chat_request: ChatRequest, request: Request) -> ChatResponse:
    """
    Process a renter's message and return an appropriate reply with next action.
    """
    # Log the request body at DEBUG level
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.debug(f"Processing chat request - ID: {request_id}")
    logger.debug(f"  Lead: {chat_request.lead.name} ({chat_request.lead.email})")
    logger.debug(f"  Message: {chat_request.message}")
    logger.debug(f"  Community: {chat_request.community_id}")
    logger.debug(f"  Preferences: {chat_request.preferences}")
    
    try:
        response = await agent_service.process_message(chat_request)
        logger.debug(f"Generated response - ID: {request_id}")
        logger.debug(f"  Reply: {response.reply}")
        logger.debug(f"  Action: {response.action}")
        logger.debug(f"  Proposed Time: {response.proposed_time}")
        return response
    except Exception as e:
        logger.error(f"Error processing chat request - ID: {request_id}, Error: {str(e)}")
        raise

@router.get("/api/memory/stats")
async def get_memory_stats():
    """
    Get agent memory statistics.
    """
    return agent_service.get_memory_stats()

@router.get("/api/conversation/{client_id}")
async def get_conversation_history(client_id: str):
    """
    Get conversation history for a client.
    """
    history = agent_service.get_conversation_history(client_id)
    return {"client_id": client_id, "messages": history}

@router.delete("/api/memory/{client_id}")
async def clear_client_memory(client_id: str):
    """
    Clear memory for a specific client.
    """
    success = agent_service.clear_client_memory(client_id)
    return {"success": success, "client_id": client_id}