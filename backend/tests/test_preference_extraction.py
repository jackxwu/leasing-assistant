"""
Unit tests for preference extraction integration.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.schemas import ChatRequest, ClientPreferences, Lead
from app.services.agent import AgentService, ClientMemory
from app.services.preference_extractor import PreferenceExtractor


class TestPreferenceExtraction:
    """Test preference extraction functionality."""

    @pytest.fixture
    def mock_preference_extractor(self):
        """Create a mock preference extractor."""
        extractor = MagicMock(spec=PreferenceExtractor)
        extractor.extract_preferences = AsyncMock(return_value={
            "bedrooms": 2,
            "max_rent": 2000,
            "has_pets": True,
            "pet_types": ["cat"]
        })
        extractor.update_preferences = MagicMock(return_value=ClientPreferences(
            bedrooms=2,
            max_rent=2000,
            has_pets=True,
            pet_types=["cat"],
            confidence_scores={"bedrooms": 0.95, "max_rent": 0.90, "has_pets": 0.95}
        ))
        return extractor

    @pytest.fixture
    def client_memory(self, mock_preference_extractor):
        """Create a client memory instance with mock extractor."""
        return ClientMemory(preference_extractor=mock_preference_extractor)

    @pytest.mark.asyncio
    async def test_add_message_extracts_preferences(self, client_memory, mock_preference_extractor):
        """Test that add_message extracts preferences from user messages."""
        # Add a user message
        await client_memory.add_message("user", "I need a 2-bedroom apartment, budget is $2000, I have a cat")
        
        # Verify message was added
        assert len(client_memory.messages) == 1
        assert client_memory.messages[0]["role"] == "user"
        
        # Verify preference extraction was called
        mock_preference_extractor.extract_preferences.assert_called_once()
        mock_preference_extractor.update_preferences.assert_called_once()
        
        # Verify preferences were updated
        assert client_memory.preferences.bedrooms == 2
        assert client_memory.preferences.max_rent == 2000
        assert client_memory.preferences.has_pets == True
        assert "cat" in client_memory.preferences.pet_types

    @pytest.mark.asyncio
    async def test_add_message_skips_assistant_messages(self, client_memory, mock_preference_extractor):
        """Test that assistant messages don't trigger preference extraction."""
        # Add an assistant message
        await client_memory.add_message("assistant", "I can help you find a 2-bedroom apartment!")
        
        # Verify message was added but no preference extraction occurred
        assert len(client_memory.messages) == 1
        mock_preference_extractor.extract_preferences.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_message_handles_extraction_errors(self, mock_preference_extractor):
        """Test that errors in preference extraction are handled gracefully."""
        # Mock extractor to raise an exception
        mock_preference_extractor.extract_preferences.side_effect = Exception("API Error")
        
        client_memory = ClientMemory(preference_extractor=mock_preference_extractor)
        
        # This should not raise an exception
        await client_memory.add_message("user", "I need an apartment")
        
        # Message should still be added
        assert len(client_memory.messages) == 1

    @pytest.mark.asyncio
    async def test_client_memory_without_extractor(self):
        """Test that ClientMemory works without preference extractor."""
        client_memory = ClientMemory(preference_extractor=None)
        
        # Should work without errors
        await client_memory.add_message("user", "I need an apartment")
        
        assert len(client_memory.messages) == 1
        # Preferences should remain default
        assert client_memory.preferences.bedrooms is None

    @pytest.mark.asyncio
    async def test_conversation_context_used(self, client_memory, mock_preference_extractor):
        """Test that conversation context is passed to preference extraction."""
        # Add some conversation history
        await client_memory.add_message("assistant", "Hello! How can I help you?")
        await client_memory.add_message("user", "I'm looking for an apartment")
        await client_memory.add_message("assistant", "What's your budget?")
        
        # Reset mock to track the next call
        mock_preference_extractor.extract_preferences.reset_mock()
        
        # Add another user message
        await client_memory.add_message("user", "My budget is $2500")
        
        # Verify context was passed
        call_args = mock_preference_extractor.extract_preferences.call_args
        message, context = call_args[0]
        
        assert message == "My budget is $2500"
        assert "assistant: What's your budget?" in context

    def test_preference_extractor_initialization(self):
        """Test that PreferenceExtractor initializes correctly."""
        extractor = PreferenceExtractor(api_key="test-key")
        assert extractor.model == "claude-3-haiku-20240307"
        assert extractor.client is not None

    @pytest.mark.asyncio 
    async def test_extract_preferences_empty_response(self):
        """Test handling of empty preference extraction response."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            # Mock empty response
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="{}")]
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            extractor = PreferenceExtractor(api_key="test-key")
            result = await extractor.extract_preferences("Hello there")
            
            assert result == {}

    def test_update_preferences_merging(self):
        """Test that preferences are merged correctly."""
        extractor = PreferenceExtractor(api_key="test-key")
        
        # Start with existing preferences
        current_prefs = ClientPreferences(
            bedrooms=1,
            pet_types=["dog"],
            amenity_priorities=["gym"]
        )
        
        # New extracted preferences
        extracted_prefs = {
            "bedrooms": 2,  # Should overwrite
            "pet_types": ["cat"],  # Should merge
            "amenity_priorities": ["pool"],  # Should merge
            "max_rent": 2000  # Should add new
        }
        
        updated_prefs = extractor.update_preferences(
            current_prefs, 
            extracted_prefs, 
            "I need a 2-bedroom with pool, I have a cat, budget $2000"
        )
        
        assert updated_prefs.bedrooms == 2
        assert set(updated_prefs.pet_types) == {"dog", "cat"}
        assert set(updated_prefs.amenity_priorities) == {"gym", "pool"}
        assert updated_prefs.max_rent == 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])