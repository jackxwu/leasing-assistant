"""
Tests for domain tools.
"""

import pytest
import tempfile
import json
import shutil
import os

from tools.tools import check_availability, check_pet_policy, get_pricing
from data import InventoryService


@pytest.fixture
def test_data_dir():
    """Create temporary directory with test data for tools."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test data matching what the tools expect
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
            },
            {
                "unit_id": "8A",
                "bedrooms": 1,
                "bathrooms": 1,
                "sqft": 750,
                "description": "Modern 1-bedroom with in-unit laundry",
                "floor": 8,
                "available_date": "2025-06-30",
                "base_rent": 1800,
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
def setup_inventory_for_tools(test_data_dir, monkeypatch):
    """Set up inventory service for tools testing."""
    # Create inventory service with test data
    inventory_service = InventoryService.from_json_files(test_data_dir)
    
    # Patch the global inventory variable in tools module
    import tools.tools
    monkeypatch.setattr(tools.tools, 'inventory', inventory_service)
    
    return inventory_service


class TestCheckAvailability:
    """Test check_availability tool function."""
    
    def test_check_availability_with_available_units(self, setup_inventory_for_tools):
        """Test check_availability when units are available."""
        result = check_availability("sunset-ridge", 2)
        
        assert result["available"] is True
        assert result["count"] == 2  # There are 2 two-bedroom units: 12B and 4D
        assert result["community_id"] == "sunset-ridge"
        assert result["bedrooms"] == 2
        assert len(result["units"]) == 2
        unit_ids = [unit["unit_id"] for unit in result["units"]]
        assert "12B" in unit_ids
        assert "4D" in unit_ids
    
    def test_check_availability_different_bedroom_counts(self, setup_inventory_for_tools):
        """Test check_availability with different bedroom counts."""
        # Test 1-bedroom
        result_1br = check_availability("sunset-ridge", 1)
        assert result_1br["available"] is True
        assert result_1br["count"] == 1
        assert result_1br["units"][0]["unit_id"] == "8A"
        
        # Test 2-bedroom
        result_2br = check_availability("sunset-ridge", 2)
        assert result_2br["available"] is True
        assert result_2br["count"] == 2  # There are 2 two-bedroom units: 12B and 4D
        unit_ids = [unit["unit_id"] for unit in result_2br["units"]]
        assert "12B" in unit_ids
        assert "4D" in unit_ids
    
    def test_check_availability_no_units(self, setup_inventory_for_tools):
        """Test check_availability when no units are available."""
        result = check_availability("sunset-ridge", 4)  # Test 4-bedroom (no 4-bedroom units exist)
        
        assert result["available"] is False
        assert "No 4-bedroom units available" in result["message"]
        assert len(result["units"]) == 0
    
    def test_check_availability_invalid_community(self, setup_inventory_for_tools):
        """Test check_availability with non-existent community."""
        result = check_availability("non-existent", 2)
        
        assert result["available"] is False
        assert len(result["units"]) == 0


class TestCheckPetPolicy:
    """Test check_pet_policy tool function."""
    
    def test_check_pet_policy_allowed_cats(self, setup_inventory_for_tools):
        """Test check_pet_policy for allowed cats."""
        result = check_pet_policy("sunset-ridge", "cats")
        
        assert result["allowed"] is True
        assert result["community_id"] == "sunset-ridge"
        assert result["pet_type"] == "cats"
        assert result["fee"] == 50
        assert result["deposit"] == 200
        assert result["monthly_rent"] == 25
    
    def test_check_pet_policy_allowed_dogs(self, setup_inventory_for_tools):
        """Test check_pet_policy for allowed dogs."""
        result = check_pet_policy("sunset-ridge", "dogs")
        
        assert result["allowed"] is True
        assert result["community_id"] == "sunset-ridge"
        assert result["pet_type"] == "dogs"
        assert result["fee"] == 75
        assert result["deposit"] == 300
        assert result["monthly_rent"] == 50
    
    def test_check_pet_policy_invalid_community(self, setup_inventory_for_tools):
        """Test check_pet_policy with non-existent community."""
        result = check_pet_policy("non-existent", "cats")
        
        assert result["allowed"] is False
        assert "Community not found" in result.get("notes", "")
    
    def test_check_pet_policy_invalid_pet_type(self, setup_inventory_for_tools):
        """Test check_pet_policy with non-existent pet type."""
        result = check_pet_policy("sunset-ridge", "elephants")
        
        assert result["allowed"] is False
        assert "Policy for elephants not defined" in result.get("notes", "")


class TestGetPricing:
    """Test get_pricing tool function."""
    
    def test_get_pricing_valid_unit(self, setup_inventory_for_tools):
        """Test get_pricing for valid unit."""
        result = get_pricing("sunset-ridge", "12B", "2025-07-15")
        
        assert result is not None
        assert result["community_id"] == "sunset-ridge"
        assert result["unit_id"] == "12B"
        assert result["move_in_date"] == "2025-07-15"
        assert "pricing" in result
        assert result["pricing"]["base_rent"] == 2400
        assert "unit_details" in result
        assert "lease_terms" in result
        assert "available_date" in result
    
    def test_get_pricing_different_units(self, setup_inventory_for_tools):
        """Test get_pricing for different units."""
        result_12b = get_pricing("sunset-ridge", "12B", "2025-07-15")
        result_8a = get_pricing("sunset-ridge", "8A", "2025-06-30")
        
        assert result_12b["pricing"]["base_rent"] == 2400
        assert result_8a["pricing"]["base_rent"] == 1800
    
    def test_get_pricing_invalid_unit(self, setup_inventory_for_tools):
        """Test get_pricing for non-existent unit."""
        result = get_pricing("sunset-ridge", "Z999", "2025-07-15")
        
        assert "error" in result
        assert result["available"] is False
        assert "Unit Z999 not found in sunset-ridge" in result["error"]
    
    def test_get_pricing_invalid_community(self, setup_inventory_for_tools):
        """Test get_pricing for non-existent community."""
        result = get_pricing("non-existent", "12B", "2025-07-15")
        
        assert "error" in result
        assert result["available"] is False
        assert "Unit 12B not found in non-existent" in result["error"]