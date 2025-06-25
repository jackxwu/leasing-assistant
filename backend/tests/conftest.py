"""
Pytest configuration and shared fixtures.
"""

import pytest
import asyncio
import os
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing."""
    # Set test environment variables
    os.environ["CLAUDE_API_KEY"] = "test-api-key-12345"
    os.environ["ENVIRONMENT"] = "test"
    
    yield
    
    # Clean up after tests
    if "CLAUDE_API_KEY" in os.environ:
        del os.environ["CLAUDE_API_KEY"]
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]


@pytest.fixture
def sample_chat_request():
    """Provide a sample chat request for testing."""
    return {
        "lead": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "message": "Do you have any 2-bedroom apartments available?",
        "preferences": {
            "bedrooms": 2,
            "move_in": "2025-08-01",
            "max_rent": 2500,
            "pet_friendly": True
        },
        "community_id": "sunset-ridge"
    }


@pytest.fixture
def sample_chat_response():
    """Provide a sample chat response for testing."""
    return {
        "reply": "Hi John! Yes, we have 2-bedroom apartments available. Would you like to schedule a tour?",
        "action": "propose_tour",
        "proposed_time": "2025-06-27T14:00:00Z"
    }