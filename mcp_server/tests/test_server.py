"""
Tests for server call_tool functionality.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
import os

from server import handle_tool_call
from data import InventoryService


@pytest.fixture
def test_data_dir():
    """Create temporary directory with test data for server tests."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test data matching what the server expects
    communities_data = {
        "sunset-ridge": {
            "name": "Sunset Ridge Apartments",
            "location": "Downtown",
            "amenities": ["pool", "gym", "parking"]
        }
    }
    
    units_data = {
        "sunset-ridge": [
            {
                "unit_id": "12B",
                "bedrooms": 2,
                "bathrooms": 2,
                "sqft": 1100,
                "description": "Corner unit with balcony and city views",
                "floor": 12,
                "available_date": "2025-07-15",
                "base_rent": 2400,
                "available": True
            }
        ]
    }
    
    pet_policies_data = {
        "sunset-ridge": {
            "cats": {
                "allowed": True,
                "fee": 50,
                "deposit": 200,
                "monthly_rent": 25,
                "max_pets": 2
            },
            "dogs": {
                "allowed": True,
                "fee": 75,
                "deposit": 300,
                "monthly_rent": 50,
                "max_pets": 2,
                "weight_limit": 60
            },
            "fish": {
                "allowed": True,
                "fee": 0,
                "deposit": 0,
                "monthly_rent": 0,
                "max_pets": 5
            }
        }
    }
    
    specials_data = [
        {
            "name": "Summer Special",
            "discount_type": "percentage",
            "amount": 10,
            "expires": "2025-08-31"
        }
    ]
    
    # Write test data files
    with open(os.path.join(temp_dir, "communities.json"), "w") as f:
        json.dump(communities_data, f)
    
    with open(os.path.join(temp_dir, "units.json"), "w") as f:
        json.dump(units_data, f)
    
    with open(os.path.join(temp_dir, "pet_policies.json"), "w") as f:
        json.dump(pet_policies_data, f)
    
    with open(os.path.join(temp_dir, "specials.json"), "w") as f:
        json.dump(specials_data, f)
    
    yield temp_dir
    
    shutil.rmtree(temp_dir)


@pytest.fixture
def setup_inventory_for_server(test_data_dir, monkeypatch):
    """Set up inventory service for server testing."""
    # Create inventory service with test data
    inventory_service = InventoryService.from_json_files(test_data_dir)
    
    # Patch the global inventory variable in tools module
    import tools.tools
    monkeypatch.setattr(tools.tools, 'inventory', inventory_service)
    
    return inventory_service


class TestServerCallTool:
    """Test server handle_tool_call functionality."""
    
    def test_handle_tool_call_check_pet_policy_fish(self, setup_inventory_for_server):
        """Test server handle_tool_call with check_pet_policy for fish."""
        # Test the specific case requested
        result = handle_tool_call(
            name="check_pet_policy",
            arguments={'community_id': 'sunset-ridge', 'pet_type': 'fish'}
        )
        
        # Verify the CallToolResult structure
        assert hasattr(result, 'content')
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        
        # Parse the JSON response
        response_data = json.loads(result.content[0].text)
        
        # Verify the response content
        assert response_data["community_id"] == "sunset-ridge"
        assert response_data["pet_type"] == "fish"
        assert response_data["allowed"] is True
        assert response_data["fee"] == 0
        assert response_data["deposit"] == 0
        assert response_data["monthly_rent"] == 0
    
    def test_handle_tool_call_check_pet_policy_invalid_pet(self, setup_inventory_for_server):
        """Test server handle_tool_call with check_pet_policy for invalid pet type."""
        result = handle_tool_call(
            name="check_pet_policy",
            arguments={'community_id': 'sunset-ridge', 'pet_type': 'elephant'}
        )
        
        # Verify the CallToolResult structure
        assert hasattr(result, 'content')
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        
        # Parse the JSON response
        response_data = json.loads(result.content[0].text)
        
        # Verify the response content for invalid pet type
        assert response_data["community_id"] == "sunset-ridge"
        assert response_data["pet_type"] == "elephant"
        assert response_data["allowed"] is False
        assert "Policy for elephant not defined" in response_data["notes"]
    
    def test_handle_tool_call_invalid_tool_name(self, setup_inventory_for_server):
        """Test server handle_tool_call with invalid tool name."""
        result = handle_tool_call(
            name="invalid_tool",
            arguments={'some_arg': 'some_value'}
        )
        
        # Verify the CallToolResult structure for error case
        assert hasattr(result, 'content')
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        
        # Verify error message
        assert "Error: Unknown tool: invalid_tool" in result.content[0].text
    
    def test_handle_tool_call_missing_arguments(self, setup_inventory_for_server):
        """Test server handle_tool_call with missing required arguments."""
        result = handle_tool_call(
            name="check_pet_policy",
            arguments={'community_id': 'sunset-ridge'}  # Missing pet_type
        )
        
        # Verify the CallToolResult structure for error case
        assert hasattr(result, 'content')
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        
        # Verify error message contains KeyError information
        assert "Error:" in result.content[0].text