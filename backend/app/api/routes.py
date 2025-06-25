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
        response = agent_service.process_message(chat_request)
        logger.debug(f"Generated response - ID: {request_id}")
        logger.debug(f"  Reply: {response.reply}")
        logger.debug(f"  Action: {response.action}")
        logger.debug(f"  Proposed Time: {response.proposed_time}")
        return response
    except Exception as e:
        logger.error(f"Error processing chat request - ID: {request_id}, Error: {str(e)}")
        raise