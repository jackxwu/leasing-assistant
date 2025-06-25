"""
Tests for InventoryService main methods.
"""

import pytest
import tempfile
import json
import os
import shutil

from data import InventoryService


@pytest.fixture
def temp_data_dir():
    """Create temporary directory with test JSON data files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample JSON data files
    communities_data = {
        "sunset-ridge": {
            "name": "Sunset Ridge Apartments",
            "location": "Downtown",
            "amenities": ["pool", "gym", "parking"]
        },
        "oak-valley": {
            "name": "Oak Valley",
            "location": "Suburbs",
            "amenities": ["pool", "parking"]
        }
    }
    
    units_data = {
        "sunset-ridge": [
            {
                "unit_id": "12B",
                "bedrooms": 2,
                "bathrooms": 2,
                "sqft": 1100,
                "description": "Corner unit with balcony",
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
                "description": "Modern 1-bedroom",
                "floor": 8,
                "available_date": "2025-06-30",
                "base_rent": 1800,
                "available": True
            }
        ],
        "oak-valley": [
            {
                "unit_id": "101",
                "bedrooms": 3,
                "bathrooms": 2,
                "sqft": 1300,
                "description": "Spacious 3-bedroom",
                "floor": 1,
                "available_date": "2025-08-01",
                "base_rent": 2800,
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
        },
        "oak-valley": {
            "cats": {
                "allowed": False,
                "notes": "No cats allowed"
            },
            "dogs": {
                "allowed": True,
                "fee": 100,
                "deposit": 400,
                "monthly_rent": 75
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
    
    # Write test data to temporary files
    with open(os.path.join(temp_dir, "communities.json"), "w") as f:
        json.dump(communities_data, f)
    
    with open(os.path.join(temp_dir, "units.json"), "w") as f:
        json.dump(units_data, f)
    
    with open(os.path.join(temp_dir, "pet_policies.json"), "w") as f:
        json.dump(pet_policies_data, f)
    
    with open(os.path.join(temp_dir, "specials.json"), "w") as f:
        json.dump(specials_data, f)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def inventory_service(temp_data_dir):
    """Create InventoryService instance with test data."""
    return InventoryService.from_json_files(temp_data_dir)


class TestGetAvailableUnits:
    """Test get_available_units method."""
    
    def test_get_units_existing_community_with_units(self, inventory_service):
        """Test getting units for existing community with available units."""
        units = inventory_service.get_available_units("sunset-ridge", 2)
        assert len(units) == 1
        assert units[0]["unit_id"] == "12B"
        assert units[0]["bedrooms"] == 2
        
    def test_get_units_existing_community_different_bedrooms(self, inventory_service):
        """Test getting units with different bedroom counts."""
        units_1br = inventory_service.get_available_units("sunset-ridge", 1)
        assert len(units_1br) == 1
        assert units_1br[0]["unit_id"] == "8A"
        
        units_3br = inventory_service.get_available_units("oak-valley", 3)
        assert len(units_3br) == 1
        assert units_3br[0]["unit_id"] == "101"
        
    def test_get_units_no_matching_bedrooms(self, inventory_service):
        """Test getting units when no units match bedroom count."""
        units = inventory_service.get_available_units("sunset-ridge", 4)
        assert len(units) == 0
        
    def test_get_units_nonexistent_community(self, inventory_service):
        """Test getting units for non-existent community."""
        units = inventory_service.get_available_units("nonexistent", 2)
        assert len(units) == 0


class TestGetPetPolicy:
    """Test get_pet_policy method."""
    
    def test_get_policy_allowed_pet(self, inventory_service):
        """Test getting policy for allowed pet type."""
        policy = inventory_service.get_pet_policy("sunset-ridge", "cats")
        assert policy["allowed"] is True
        assert policy["fee"] == 50
        assert policy["deposit"] == 200
        assert policy["monthly_rent"] == 25
        
    def test_get_policy_not_allowed_pet(self, inventory_service):
        """Test getting policy for not allowed pet type."""
        policy = inventory_service.get_pet_policy("oak-valley", "cats")
        assert policy["allowed"] is False
        assert "No cats allowed" in policy["notes"]
        
    def test_get_policy_different_pet_types(self, inventory_service):
        """Test getting policies for different pet types."""
        dog_policy = inventory_service.get_pet_policy("sunset-ridge", "dogs")
        assert dog_policy["allowed"] is True
        assert dog_policy["fee"] == 75
        
        cat_policy = inventory_service.get_pet_policy("sunset-ridge", "cats")
        assert cat_policy["allowed"] is True
        assert cat_policy["fee"] == 50
        
    def test_get_policy_nonexistent_community(self, inventory_service):
        """Test getting policy for non-existent community."""
        policy = inventory_service.get_pet_policy("nonexistent", "cats")
        assert policy["allowed"] is False
        assert "Community not found" in policy["notes"]
        
    def test_get_policy_nonexistent_pet_type(self, inventory_service):
        """Test getting policy for non-existent pet type."""
        policy = inventory_service.get_pet_policy("sunset-ridge", "elephants")
        assert policy["allowed"] is False
        assert "Policy for elephants not defined" in policy["notes"]


class TestGetPricing:
    """Test get_pricing method."""
    
    def test_get_pricing_valid_unit(self, inventory_service):
        """Test getting pricing for valid unit and date."""
        pricing = inventory_service.get_pricing("sunset-ridge", "12B", "2025-07-15")
        assert pricing is not None
        assert pricing["unit_id"] == "12B"
        assert pricing["community_id"] == "sunset-ridge"
        assert pricing["move_in_date"] == "2025-07-15"
        assert pricing["pricing"]["base_rent"] == 2400
        
    def test_get_pricing_different_units(self, inventory_service):
        """Test getting pricing for different units."""
        pricing_12b = inventory_service.get_pricing("sunset-ridge", "12B", "2025-07-15")
        assert pricing_12b["pricing"]["base_rent"] == 2400
        
        pricing_8a = inventory_service.get_pricing("sunset-ridge", "8A", "2025-06-30")
        assert pricing_8a["pricing"]["base_rent"] == 1800
        
        pricing_101 = inventory_service.get_pricing("oak-valley", "101", "2025-08-01")
        assert pricing_101["pricing"]["base_rent"] == 2800
        
    def test_get_pricing_different_dates(self, inventory_service):
        """Test getting pricing for different move-in dates."""
        pricing1 = inventory_service.get_pricing("sunset-ridge", "12B", "2025-07-15")
        pricing2 = inventory_service.get_pricing("sunset-ridge", "12B", "2025-08-01")
        
        assert pricing1 is not None
        assert pricing2 is not None
        assert pricing1["move_in_date"] == "2025-07-15"
        assert pricing2["move_in_date"] == "2025-08-01"
        
    def test_get_pricing_nonexistent_unit(self, inventory_service):
        """Test getting pricing for non-existent unit."""
        pricing = inventory_service.get_pricing("sunset-ridge", "Z999", "2025-07-15")
        assert pricing is None
        
    def test_get_pricing_nonexistent_community(self, inventory_service):
        """Test getting pricing for non-existent community."""
        pricing = inventory_service.get_pricing("nonexistent", "12B", "2025-07-15")
        assert pricing is None