#!/usr/bin/env python3
"""
Leasing Assistant MCP Server

This server provides tools for apartment leasing operations:
- check_availability: Check unit availability by community and bedroom count
- check_pet_policy: Check pet policies for specific communities
- get_pricing: Get pricing information for units and move-in dates
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    TextContent,
    Tool,
)

from data import InventoryService
from tools import check_availability, check_pet_policy, get_pricing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize inventory service
inventory = InventoryService()

# Create MCP server
server = Server("leasing-assistant")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the leasing assistant."""
    logger.info("list_tools called")
    return [
        Tool(
            name="check_availability",
            description="Check apartment unit availability by community and bedroom count",
            inputSchema={
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
        ),
        Tool(
            name="check_pet_policy",
            description="Check pet policy for a specific community and pet type",
            inputSchema={
                "type": "object",
                "properties": {
                    "community_id": {
                        "type": "string",
                        "description": "Community identifier (e.g., 'sunset-ridge')"
                    },
                    "pet_type": {
                        "type": "string",
                        "description": "Type of pet (e.g., 'cat', 'dog', 'bird')",
                        "enum": ["cat", "dog", "bird", "fish", "small_pet"]
                    }
                },
                "required": ["community_id", "pet_type"]
            }
        ),
        Tool(
            name="get_pricing",
            description="Get pricing information for a specific unit and move-in date",
            inputSchema={
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
        )
    ]

def handle_tool_call(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Synchronous tool call handler for easier testing."""
    logger.info(f"name={name}, arguments={arguments}")
    try:
        if name == "check_availability":
            result = check_availability(
                community_id=arguments["community_id"],
                bedrooms=arguments["bedrooms"]
            )
        elif name == "check_pet_policy":
            result = check_pet_policy(
                community_id=arguments["community_id"], 
                pet_type=arguments["pet_type"]
            )
        elif name == "get_pricing":
            result = get_pricing(
                community_id=arguments["community_id"],
                unit_id=arguments["unit_id"],
                move_in_date=arguments["move_in_date"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        logger.info(f"name={name}, tool result={result}")
        
        # Workaround for MCP stdio serialization bug #987
        # Create CallToolResult using from_dict or minimal construction
        result_json = json.dumps(result, indent=2)
        
        # Try creating CallToolResult with minimal fields to avoid serialization issues
        try:
            call_result = CallToolResult(content=[TextContent(type="text", text=result_json)])
            logger.info(f"name={name}, call_result created: {type(call_result)}")
            return call_result
        except Exception as construction_error:
            logger.error(f"CallToolResult construction failed: {construction_error}")
            # Fallback: return the raw result and let MCP handle it
            return result
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        
        # Workaround for MCP stdio serialization bug #987
        # Create error result with minimal construction
        try:
            error_result = CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])
            logger.info(f"name={name}, error_result created: {type(error_result)}")
            return error_result
        except Exception as construction_error:
            logger.error(f"Error CallToolResult construction failed: {construction_error}")
            # Fallback: return simple error dict
            return {"error": str(e)}


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for leasing operations."""
    return handle_tool_call(name, arguments)


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Leasing Assistant MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="leasing-assistant",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def run_server():
    """Entry point for running the server."""
    asyncio.run(main())

if __name__ == "__main__":
    run_server()