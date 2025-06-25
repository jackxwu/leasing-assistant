"""
Agent service that routes to appropriate LLM implementation.
"""

import asyncio
import logging
from typing import Optional
from app.models.schemas import ChatRequest, ChatResponse
from app.core.config import config
from app.services.claude_agent import ClaudeAgentService

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self._claude_agent: Optional[ClaudeAgentService] = None
        self._initialized = False
    
    async def _initialize_if_needed(self):
        """Initialize the agent service if not already done."""
        if self._initialized:
            return
        
        # Get Claude API key from config
        claude_api_key = config.get("llm.claude_api_key")
        if not claude_api_key:
            raise ValueError("CLAUDE_API_KEY environment variable is required")
        
        # Initialize Claude agent
        self._claude_agent = ClaudeAgentService(api_key=claude_api_key)
        await self._claude_agent.initialize()
        
        self._initialized = True
        logger.info("Agent service initialized with Claude backend")
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message using Claude LLM with MCP tools."""
        await self._initialize_if_needed()
        
        try:
            return await self._claude_agent.process_message(request)
        except Exception as e:
            logger.error(f"Error in agent service: {e}")
            
            # Fallback response
            lead_name = request.lead.name.split()[0]
            return ChatResponse(
                reply=f"Hi {lead_name}! I apologize, but I'm experiencing technical difficulties. Let me connect you with one of our leasing specialists who can assist you immediately.",
                action="handoff_human"
            )
    
    def process_message_sync(self, request: ChatRequest) -> ChatResponse:
        """Synchronous wrapper for process_message."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_message(request))
    
    async def cleanup(self):
        """Clean up agent service resources."""
        if self._claude_agent:
            await self._claude_agent.cleanup()
        self._initialized = False
        logger.info("Agent service cleaned up")