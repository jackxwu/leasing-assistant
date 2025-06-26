"""
MCP Client for connecting to the leasing assistant MCP server.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp_server"
        self.server_process = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the MCP client connection."""
        if self.initialized:
            return
        
        try:
            # For now, we'll use direct function calls since MCP stdio can be complex
            # In a production environment, we will use proper MCP stdio communication
            logger.info("MCP Client initialized (using direct function calls)")
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Import the tools directly for now
            # In production, this would be proper MCP protocol communication
            import sys
            sys.path.append(str(self.mcp_server_path))
            
            if tool_name == "check_availability":
                from tools.tools import check_availability
                result = check_availability(
                    community_id=arguments["community_id"],
                    bedrooms=arguments["bedrooms"]
                )
            elif tool_name == "check_pet_policy":
                from tools.tools import check_pet_policy
                result = check_pet_policy(
                    community_id=arguments["community_id"],
                    pet_type=arguments["pet_type"]
                )
            elif tool_name == "get_pricing":
                from tools.tools import get_pricing
                result = get_pricing(
                    community_id=arguments["community_id"],
                    unit_id=arguments["unit_id"],
                    move_in_date=arguments["move_in_date"]
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            logger.info(f"MCP tool {tool_name} called. result is: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            raise
    
    async def check_availability(self, community_id: str, bedrooms: int) -> Dict[str, Any]:
        """Check apartment availability."""
        return await self.call_tool("check_availability", {
            "community_id": community_id,
            "bedrooms": bedrooms
        })
    
    async def check_pet_policy(self, community_id: str, pet_type: str) -> Dict[str, Any]:
        """Check pet policy."""
        return await self.call_tool("check_pet_policy", {
            "community_id": community_id,
            "pet_type": pet_type
        })
    
    async def get_pricing(self, community_id: str, unit_id: str, move_in_date: str) -> Dict[str, Any]:
        """Get pricing information."""
        return await self.call_tool("get_pricing", {
            "community_id": community_id,
            "unit_id": unit_id,
            "move_in_date": move_in_date
        })
    
    async def cleanup(self):
        """Clean up MCP client resources."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error cleaning up MCP server process: {e}")
        
        self.initialized = False
        logger.info("MCP Client cleaned up")

# Global MCP client instance
mcp_client = MCPClient()