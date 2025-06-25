"""
Claude-powered agent service with MCP tool integration.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import anthropic
from anthropic.types import MessageParam, ToolUseBlock, ToolParam
from app.models.schemas import ChatRequest, ChatResponse
from app.services.mcp_client import mcp_client

logger = logging.getLogger(__name__)

class ClaudeAgentService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        
        # Define the tools available to Claude
        self.tools: List[ToolParam] = [
            {
                "name": "check_availability",
                "description": "Check apartment unit availability by community and bedroom count",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "community_id": {
                            "type": "string",
                            "description": "Community identifier (e.g., 'sunset-ridge')"
                        },
                        "bedrooms": {
                            "type": "integer",
                            "description": "Number of bedrooms required",
                            "minimum": 1,
                            "maximum": 4
                        }
                    },
                    "required": ["community_id", "bedrooms"]
                }
            },
            {
                "name": "check_pet_policy",
                "description": "Check pet policy for a specific community and pet type",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "community_id": {
                            "type": "string",
                            "description": "Community identifier (e.g., 'sunset-ridge')"
                        },
                        "pet_type": {
                            "type": "string",
                            "description": "Type of pet (e.g., 'cat', 'dog', 'bird', 'fish', 'small_pet')",
                            "enum": ["cat", "dog", "bird", "fish", "small_pet"]
                        }
                    },
                    "required": ["community_id", "pet_type"]
                }
            },
            {
                "name": "get_pricing",
                "description": "Get pricing information for a specific unit and move-in date",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "community_id": {
                            "type": "string",
                            "description": "Community identifier"
                        },
                        "unit_id": {
                            "type": "string",
                            "description": "Unit identifier (e.g., '12B')"
                        },
                        "move_in_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Desired move-in date (YYYY-MM-DD)"
                        }
                    },
                    "required": ["community_id", "unit_id", "move_in_date"]
                }
            }
        ]
    
    async def initialize(self):
        """Initialize the agent service."""
        await mcp_client.initialize()
        logger.info("Claude Agent Service initialized")
    
    def _create_system_prompt(self, community_id: str, lead_name: str) -> str:
        """Create the system prompt for Claude."""
        community_display = community_id.replace('-', ' ').title()
        
        return f"""You are a helpful leasing assistant for {community_display} apartments. Your goal is to help prospective renters find their perfect home.

Lead Information:
- Lead name: {lead_name}
- Community: {community_display}

Your Role:
- Be friendly, professional, and helpful
- Use the lead's first name when appropriate
- Always prioritize the lead's needs and preferences
- Provide accurate information using the available tools
- Guide conversations toward scheduling tours when appropriate

Available Actions:
- "propose_tour": When you want to suggest scheduling a tour (include a proposed_time)
- "ask_clarification": When you need more information from the lead
- "handoff_human": When the inquiry is complex or requires human assistance

Guidelines:
- Always check availability, pet policies, and pricing using the provided tools
- Be specific about dates, prices, and unit details
- If you don't have information, use tools to get it or suggest connecting with a specialist
- Keep responses conversational but informative
- Focus on benefits and features that match the lead's needs

Remember: You have access to real-time data through tools, so use them to provide accurate information."""
    
    async def _execute_tool_calls(self, tool_calls: List[ToolUseBlock]) -> List[Dict[str, Any]]:
        """Execute tool calls using MCP client."""
        results = []
        
        for tool_call in tool_calls:
            try:
                tool_name = tool_call.name
                arguments = tool_call.input
                
                if tool_name == "check_availability":
                    result = await mcp_client.check_availability(
                        community_id=arguments["community_id"],
                        bedrooms=arguments["bedrooms"]
                    )
                elif tool_name == "check_pet_policy":
                    result = await mcp_client.check_pet_policy(
                        community_id=arguments["community_id"],
                        pet_type=arguments["pet_type"]
                    )
                elif tool_name == "get_pricing":
                    result = await mcp_client.get_pricing(
                        community_id=arguments["community_id"],
                        unit_id=arguments["unit_id"],
                        move_in_date=arguments["move_in_date"]
                    )
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                results.append({
                    "tool_use_id": tool_call.id,
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_call.name}: {e}")
                results.append({
                    "tool_use_id": tool_call.id,
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}]
                })
        
        return results
    
    def _extract_action_and_time(self, response_text: str) -> tuple[str, Optional[datetime]]:
        """Extract action and proposed time from Claude's response."""
        # Simple heuristics to determine action
        text_lower = response_text.lower()
        
        # Check for tour proposals
        if any(phrase in text_lower for phrase in ["schedule a tour", "tour available", "would you like to see", "tour time"]):
            # Generate a proposed time (next few days)
            proposed_time = datetime.now() + timedelta(days=2, hours=14)  # 2 PM in 2 days
            return "propose_tour", proposed_time
        
        # Check for clarification requests
        elif any(phrase in text_lower for phrase in ["could you tell me", "what are you looking for", "more information", "help me understand"]):
            return "ask_clarification", None
        
        # Check for human handoff indicators
        elif any(phrase in text_lower for phrase in ["connect you with", "leasing specialist", "specialist", "complex"]):
            return "handoff_human", None
        
        # Default to clarification if unclear
        return "ask_clarification", None
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message using Claude and MCP tools."""
        try:
            lead_name = request.lead.name.split()[0]  # First name only
            
            # Create conversation messages
            messages: List[MessageParam] = [
                {
                    "role": "user",
                    "content": f"Lead message: {request.message}\n\nLead preferences: {request.preferences.model_dump() if request.preferences else 'None specified'}"
                }
            ]
            
            # Initial Claude API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self._create_system_prompt(request.community_id, lead_name),
                messages=messages,
                tools=self.tools
            )
            
            # Check if Claude wants to use tools
            if response.content and any(block.type == "tool_use" for block in response.content):
                # Extract tool calls
                tool_calls = [block for block in response.content if block.type == "tool_use"]
                
                # Execute tool calls
                tool_results = await self._execute_tool_calls(tool_calls)
                
                # Add tool results to conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Add tool results with correct format
                for tool_result in tool_results:
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_result["tool_use_id"],
                                "content": tool_result["content"][0]["text"]
                            }
                        ]
                    })
                
                # Get final response from Claude
                final_response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=self._create_system_prompt(request.community_id, lead_name),
                    messages=messages,
                    tools=self.tools
                )
                
                response_text = "".join([
                    block.text for block in final_response.content 
                    if hasattr(block, 'text')
                ])
            else:
                # No tools needed, use direct response
                response_text = "".join([
                    block.text for block in response.content 
                    if hasattr(block, 'text')
                ])
            
            # Extract action and proposed time
            action, proposed_time = self._extract_action_and_time(response_text)
            
            return ChatResponse(
                reply=response_text,
                action=action,
                proposed_time=proposed_time
            )
            
        except Exception as e:
            logger.error(f"Error processing message with Claude: {e}")
            
            # Fallback response
            return ChatResponse(
                reply=f"Hi {lead_name}! I apologize, but I'm having technical difficulties right now. Let me connect you with one of our leasing specialists who can assist you immediately.",
                action="handoff_human"
            )
    
    async def cleanup(self):
        """Clean up resources."""
        await mcp_client.cleanup()
        logger.info("Claude Agent Service cleaned up")