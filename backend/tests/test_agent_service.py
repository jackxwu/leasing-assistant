"""
Unit tests for the Agent Service and Claude integration.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.models.schemas import ChatRequest, ChatResponse, Lead, Preferences
from app.services.agent import AgentService
from app.services.claude_agent import ClaudeAgentService


class TestAgentService:
    """Test suite for AgentService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent_service = AgentService()
    
    @pytest.mark.asyncio
    async def test_initialization_with_valid_api_key(self):
        """Test that agent service initializes correctly with valid API key."""
        with patch('app.core.config.config.get') as mock_config:
            mock_config.return_value = "test-api-key-123"
            
            # Initialize the agent service
            await self.agent_service._initialize_if_needed()
            
            # Verify initialization
            assert self.agent_service._initialized is True
            assert self.agent_service._claude_agent is not None
            assert isinstance(self.agent_service._claude_agent, ClaudeAgentService)
    
    @pytest.mark.asyncio
    async def test_initialization_without_api_key(self):
        """Test that agent service fails to initialize without API key."""
        with patch('app.core.config.config.get') as mock_config:
            mock_config.return_value = None
            
            # Should raise ValueError when no API key
            with pytest.raises(ValueError, match="CLAUDE_API_KEY environment variable is required"):
                await self.agent_service._initialize_if_needed()
    
    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test successful message processing."""
        # Mock the Claude agent
        mock_claude_agent = AsyncMock()
        mock_response = ChatResponse(
            reply="Hi John! Yes, we have 1-bedroom apartments available.",
            action="propose_tour",
            proposed_time=None
        )
        mock_claude_agent.process_message.return_value = mock_response
        
        # Set up agent service with mock
        self.agent_service._claude_agent = mock_claude_agent
        self.agent_service._initialized = True
        
        # Create test request
        request = ChatRequest(
            lead=Lead(name="John Doe", email="john@example.com"),
            message="Do you have 1-bedroom apartments available?",
            preferences=Preferences(bedrooms=1, move_in="2025-08-01"),
            community_id="sunset-ridge"
        )
        
        # Process message
        response = await self.agent_service.process_message(request)
        
        # Verify response
        assert response.reply == "Hi John! Yes, we have 1-bedroom apartments available."
        assert response.action == "propose_tour"
        mock_claude_agent.process_message.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_process_message_fallback_on_error(self):
        """Test fallback response when Claude agent fails."""
        # Mock the Claude agent to raise an exception
        mock_claude_agent = AsyncMock()
        mock_claude_agent.process_message.side_effect = Exception("Claude API error")
        
        # Set up agent service with mock
        self.agent_service._claude_agent = mock_claude_agent
        self.agent_service._initialized = True
        
        # Create test request
        request = ChatRequest(
            lead=Lead(name="Jane Smith", email="jane@example.com"),
            message="Do you allow pets?",
            preferences=None,
            community_id="sunset-ridge"
        )
        
        # Process message
        response = await self.agent_service.process_message(request)
        
        # Verify fallback response
        assert "Jane!" in response.reply
        assert "technical difficulties" in response.reply
        assert "leasing specialists" in response.reply
        assert response.action == "handoff_human"
        assert response.proposed_time is None
    
    def test_process_message_sync(self):
        """Test synchronous wrapper for process_message."""
        # Mock the async process_message method
        expected_response = ChatResponse(
            reply="Test response",
            action="ask_clarification",
            proposed_time=None
        )
        
        with patch.object(self.agent_service, 'process_message') as mock_process:
            mock_process.return_value = expected_response
            
            # Create test request
            request = ChatRequest(
                lead=Lead(name="Test User", email="test@example.com"),
                message="Test message",
                preferences=None,
                community_id="test-community"
            )
            
            # Call sync wrapper
            response = self.agent_service.process_message_sync(request)
            
            # Verify response
            assert response == expected_response
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test agent service cleanup."""
        # Set up agent service with mock Claude agent
        mock_claude_agent = AsyncMock()
        self.agent_service._claude_agent = mock_claude_agent
        self.agent_service._initialized = True
        
        # Call cleanup
        await self.agent_service.cleanup()
        
        # Verify cleanup
        mock_claude_agent.cleanup.assert_called_once()
        assert self.agent_service._initialized is False


class TestClaudeAgentService:
    """Test suite for ClaudeAgentService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.claude_agent = ClaudeAgentService(api_key="test-api-key")
    
    def test_create_system_prompt(self):
        """Test system prompt creation."""
        prompt = self.claude_agent._create_system_prompt("sunset-ridge", "John")
        
        # Verify prompt contains expected elements
        assert "John" in prompt
        assert "Sunset Ridge" in prompt
        assert "leasing assistant" in prompt.lower()
        assert "propose_tour" in prompt
        assert "ask_clarification" in prompt
        assert "handoff_human" in prompt
    
    def test_extract_action_and_time_tour_proposal(self):
        """Test action extraction for tour proposals."""
        response_text = "Would you like to schedule a tour? I have availability this Saturday."
        
        action, proposed_time = self.claude_agent._extract_action_and_time(response_text)
        
        assert action == "propose_tour"
        assert proposed_time is not None
    
    def test_extract_action_and_time_clarification(self):
        """Test action extraction for clarification requests."""
        response_text = "Could you tell me more about your budget requirements?"
        
        action, proposed_time = self.claude_agent._extract_action_and_time(response_text)
        
        assert action == "ask_clarification"
        assert proposed_time is None
    
    def test_extract_action_and_time_handoff(self):
        """Test action extraction for human handoff."""
        response_text = "Let me connect you with one of our leasing specialists for assistance."
        
        action, proposed_time = self.claude_agent._extract_action_and_time(response_text)
        
        assert action == "handoff_human"
        assert proposed_time is None
    
    @pytest.mark.asyncio
    async def test_execute_tool_calls_availability(self):
        """Test tool execution for availability check."""
        # Mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "tool_123"
        mock_tool_call.name = "check_availability"
        mock_tool_call.input = {"community_id": "sunset-ridge", "bedrooms": 2}
        
        # Mock MCP client
        with patch('app.services.claude_agent.mcp_client') as mock_mcp:
            mock_mcp.check_availability.return_value = {
                "available_units": [{"unit_id": "12B", "available": True}],
                "community_id": "sunset-ridge",
                "bedroom_count": 2
            }
            
            # Execute tool calls
            results = await self.claude_agent._execute_tool_calls([mock_tool_call])
            
            # Verify results
            assert len(results) == 1
            assert results[0]["tool_use_id"] == "tool_123"
            assert "available_units" in results[0]["content"][0]["text"]
            mock_mcp.check_availability.assert_called_once_with(
                community_id="sunset-ridge", 
                bedrooms=2
            )
    
    @pytest.mark.asyncio
    async def test_execute_tool_calls_pet_policy(self):
        """Test tool execution for pet policy check."""
        # Mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "tool_456"
        mock_tool_call.name = "check_pet_policy"
        mock_tool_call.input = {"community_id": "sunset-ridge", "pet_type": "cat"}
        
        # Mock MCP client
        with patch('app.services.claude_agent.mcp_client') as mock_mcp:
            mock_mcp.check_pet_policy.return_value = {
                "allowed": True,
                "fee": 50,
                "deposit": 200,
                "monthly_rent": 25
            }
            
            # Execute tool calls
            results = await self.claude_agent._execute_tool_calls([mock_tool_call])
            
            # Verify results
            assert len(results) == 1
            assert results[0]["tool_use_id"] == "tool_456"
            assert "allowed" in results[0]["content"][0]["text"]
            mock_mcp.check_pet_policy.assert_called_once_with(
                community_id="sunset-ridge",
                pet_type="cat"
            )
    
    @pytest.mark.asyncio
    async def test_execute_tool_calls_unknown_tool(self):
        """Test handling of unknown tool calls."""
        # Mock tool call with unknown tool
        mock_tool_call = Mock()
        mock_tool_call.id = "tool_789"
        mock_tool_call.name = "unknown_tool"
        mock_tool_call.input = {}
        
        # Execute tool calls
        results = await self.claude_agent._execute_tool_calls([mock_tool_call])
        
        # Verify error handling
        assert len(results) == 1
        assert results[0]["tool_use_id"] == "tool_789"
        assert "Unknown tool" in results[0]["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test Claude agent cleanup."""
        with patch('app.services.claude_agent.mcp_client') as mock_mcp:
            await self.claude_agent.cleanup()
            mock_mcp.cleanup.assert_called_once()