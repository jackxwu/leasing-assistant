"""
Agent service that routes to appropriate LLM implementation.
"""

import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime
from app.models.schemas import ChatRequest, ChatResponse, ClientPreferences
from app.core.config import config
from app.services.claude_agent import ClaudeAgentService
from app.services.preference_extractor import PreferenceExtractor

logger = logging.getLogger(__name__)

class ClientMemory:
    """Stores conversation history for a client."""
    def __init__(self, preference_extractor: Optional[PreferenceExtractor] = None):
        self.messages: List[Dict[str, str]] = []
        self.lead_info: Optional[Dict] = None
        self.preferences: ClientPreferences = ClientPreferences() 
        self.community_id: Optional[str] = None
        self._preference_extractor = preference_extractor
    
    async def add_message(self, role: str, content: str):
        """Add a message to the conversation history and extract preferences if it's a user message."""
        self.messages.append({"role": role, "content": content})
        
        # Extract preferences from user messages
        if role == "user" and self._preference_extractor:
            try:
                # Get conversation context for better extraction
                context = ""
                if len(self.messages) > 1:
                    # Use last few messages as context
                    recent_messages = self.messages[-3:-1]  # Exclude current message
                    context = " ".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
                
                # Extract preferences from the message
                extracted_prefs = await self._preference_extractor.extract_preferences(content, context)
                
                if extracted_prefs:
                    # Update client preferences with extracted data
                    self.preferences = self._preference_extractor.update_preferences(
                        self.preferences, 
                        extracted_prefs, 
                        content
                    )
                    logger.info(f"Updated preferences for client: {extracted_prefs}")
                
            except Exception as e:
                logger.error(f"Error extracting preferences: {e}")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.messages.copy()
    
    def update_context(self, lead: Dict, preferences: Optional[Dict], community_id: str):
        """Update client context information."""
        self.lead_info = lead
        # Don't overwrite ClientPreferences with dict - keep the existing ClientPreferences object
        # The preferences parameter here is from the request and should be merged, not replaced
        self.community_id = community_id

class AgentService:
    def __init__(self):
        self._claude_agent: Optional[ClaudeAgentService] = None
        self._preference_extractor: Optional[PreferenceExtractor] = None
        self._initialized = False
        self._short_term_memory: Dict[str, ClientMemory] = {}
    
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
        
        # Initialize preference extractor
        self._preference_extractor = PreferenceExtractor(api_key=claude_api_key)
        
        self._initialized = True
        logger.info("Agent service initialized with Claude backend and preference extraction")
    
    def _get_or_create_client_memory(self, client_id: str) -> ClientMemory:
        """Get or create memory for a client."""
        if client_id not in self._short_term_memory:
            self._short_term_memory[client_id] = ClientMemory(preference_extractor=self._preference_extractor)
            logger.info(f"Created new memory for client: {client_id}")
        return self._short_term_memory[client_id]
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message using Claude LLM with MCP tools."""
        await self._initialize_if_needed()
        
        try:
            # Get or create client memory
            client_memory = self._get_or_create_client_memory(request.client_id)
            
            # Update client context
            client_memory.update_context(
                lead=request.lead.model_dump(),
                preferences=request.preferences.model_dump() if request.preferences else None,
                community_id=request.community_id
            )
            
            # Add user message to memory (this extracts preferences)
            await client_memory.add_message("user", request.message)
            
            # Process message with conversation history and comprehensive context
            response = await self._claude_agent.process_message(request, client_memory)
            
            # Add assistant response to memory
            await client_memory.add_message("assistant", response.reply)
            
            logger.info(f"Processed message for client {request.client_id}. Memory has {len(client_memory.messages)} messages.")
            
            return response
            
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
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get memory statistics."""
        stats = {
            "total_clients": len(self._short_term_memory),
            "total_messages": sum(len(memory.messages) for memory in self._short_term_memory.values())
        }
        return stats
    
    def get_conversation_history(self, client_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a client."""
        if client_id not in self._short_term_memory:
            return []
        
        return self._short_term_memory[client_id].get_conversation_history()
    
    def clear_client_memory(self, client_id: str) -> bool:
        """Clear memory for a specific client."""
        if client_id in self._short_term_memory:
            del self._short_term_memory[client_id]
            logger.info(f"Cleared memory for client: {client_id}")
            return True
        return False
    
    async def cleanup(self):
        """Clean up agent service resources."""
        if self._claude_agent:
            await self._claude_agent.cleanup()
        self._short_term_memory.clear()
        self._initialized = False
        logger.info("Agent service cleaned up")