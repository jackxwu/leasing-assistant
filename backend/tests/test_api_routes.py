"""
Unit tests for API routes.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ChatResponse


class TestAPIRoutes:
    """Test suite for API routes."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint returns correct information."""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "environment" in data
        assert "version" in data
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
    
    def test_reply_endpoint_success(self):
        """Test successful reply endpoint."""
        # Mock the agent service
        mock_response = ChatResponse(
            reply="Hi John! Yes, we have 1-bedroom apartments available.",
            action="propose_tour",
            proposed_time=None
        )
        
        with patch('app.api.routes.agent_service.process_message') as mock_process:
            mock_process.return_value = mock_response
            
            # Make request
            request_data = {
                "lead": {
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "message": "Do you have 1-bedroom apartments available?",
                "preferences": {
                    "bedrooms": 1,
                    "move_in": "2025-08-01"
                },
                "community_id": "sunset-ridge"
            }
            
            response = self.client.post("/api/reply", json=request_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["reply"] == "Hi John! Yes, we have 1-bedroom apartments available."
            assert data["action"] == "propose_tour"
            assert data["proposed_time"] is None
    
    def test_reply_endpoint_validation_error(self):
        """Test reply endpoint with invalid request data."""
        # Missing required fields
        request_data = {
            "lead": {
                "name": "John Doe"
                # Missing email
            },
            "message": "Test message"
            # Missing community_id
        }
        
        response = self.client.post("/api/reply", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_reply_endpoint_empty_message(self):
        """Test reply endpoint with empty message."""
        request_data = {
            "lead": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "message": "",  # Empty message
            "community_id": "sunset-ridge"
        }
        
        response = self.client.post("/api/reply", json=request_data)
        
        # Should return validation error for empty message
        assert response.status_code == 422
    
    def test_reply_endpoint_with_preferences(self):
        """Test reply endpoint with preferences."""
        mock_response = ChatResponse(
            reply="Great! I found some 2-bedroom options for you.",
            action="ask_clarification",
            proposed_time=None
        )
        
        with patch('app.api.routes.agent_service.process_message') as mock_process:
            mock_process.return_value = mock_response
            
            request_data = {
                "lead": {
                    "name": "Jane Smith",
                    "email": "jane@example.com"
                },
                "message": "I need a 2-bedroom apartment",
                "preferences": {
                    "bedrooms": 2,
                    "move_in": "2025-09-01",
                    "max_rent": 2500,
                    "pet_friendly": True
                },
                "community_id": "sunset-ridge"
            }
            
            response = self.client.post("/api/reply", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["reply"] == "Great! I found some 2-bedroom options for you."
            assert data["action"] == "ask_clarification"
    
    def test_reply_endpoint_without_preferences(self):
        """Test reply endpoint without preferences."""
        mock_response = ChatResponse(
            reply="Hello! How can I help you today?",
            action="ask_clarification",
            proposed_time=None
        )
        
        with patch('app.api.routes.agent_service.process_message') as mock_process:
            mock_process.return_value = mock_response
            
            request_data = {
                "lead": {
                    "name": "Bob Wilson",
                    "email": "bob@example.com"
                },
                "message": "Hello, I'm interested in your apartments",
                "community_id": "oak-valley"
            }
            
            response = self.client.post("/api/reply", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["reply"] == "Hello! How can I help you today?"
    
    def test_reply_endpoint_server_error(self):
        """Test reply endpoint when agent service raises an exception."""
        with patch('app.api.routes.agent_service.process_message') as mock_process:
            mock_process.side_effect = Exception("Internal server error")
            
            request_data = {
                "lead": {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "message": "Test message",
                "community_id": "test-community"
            }
            
            response = self.client.post("/api/reply", json=request_data)
            
            # Should return 500 internal server error
            assert response.status_code == 500
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = self.client.options("/api/reply")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_request_id_header(self):
        """Test that request ID is added to response headers."""
        mock_response = ChatResponse(
            reply="Test response",
            action="ask_clarification",
            proposed_time=None
        )
        
        with patch('app.api.routes.agent_service.process_message') as mock_process:
            mock_process.return_value = mock_response
            
            request_data = {
                "lead": {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "message": "Test message",
                "community_id": "test-community"
            }
            
            response = self.client.post("/api/reply", json=request_data)
            
            # Should have request ID in headers
            assert "X-Request-ID" in response.headers
            assert len(response.headers["X-Request-ID"]) > 0