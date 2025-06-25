"""
Inventory service that can load data from JSON files or database.
Provides apartment data for testing and production environments.
"""

from typing import Dict, List, Any, Optional, Protocol
from datetime import datetime, timedelta
import random
import logging
from .loader import DataLoader

# Configure logging
logger = logging.getLogger(__name__)


class DataProvider(Protocol):
    """Protocol defining the interface for data providers."""
    
    def load_communities(self) -> Dict[str, Any]:
        """Load community data."""
        ...
    
    def load_units(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load unit data."""
        ...
    
    def load_pet_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load pet policy data."""
        ...
    
    def load_specials(self) -> List[Dict[str, Any]]:
        """Load special offers data."""
        ...


class JsonFileLoader(DataLoader):
    """JSON file-based data provider implementation."""
    
    def __init__(self, data_dir: str = None):
        super().__init__(data_dir)


class DatabaseReader:
    """Database-based data provider implementation (to be implemented)."""
    
    def __init__(self, connection_string: str = None):
        """Initialize database connection (placeholder)."""
        self.connection_string = connection_string
        # TODO: Initialize database connection
    
    def load_communities(self) -> Dict[str, Any]:
        """Load community data from database."""
        # TODO: Implement database query for communities
        raise NotImplementedError("Database loading not yet implemented")
    
    def load_units(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load unit data from database."""
        # TODO: Implement database query for units
        raise NotImplementedError("Database loading not yet implemented")
    
    def load_pet_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load pet policy data from database."""
        # TODO: Implement database query for pet policies
        raise NotImplementedError("Database loading not yet implemented")
    
    def load_specials(self) -> List[Dict[str, Any]]:
        """Load special offers data from database."""
        # TODO: Implement database query for specials
        raise NotImplementedError("Database loading not yet implemented")


class InventoryService:
    """Apartment inventory service that can load data from JSON files or database."""
    
    def __init__(self, data_provider: Optional[DataProvider] = None, data_dir: str = None, connection_string: str = None):
        """
        Initialize inventory service with a data provider.
        
        Args:
            data_provider: Custom data provider instance
            data_dir: Directory for JSON files (used if data_provider is None)
            connection_string: Database connection string (for DatabaseReader)
        """

        """

        if data_provider is not None:
            self.data_provider = data_provider
        elif connection_string is not None:
            # Use database provider (placeholder for future implementation)
            self.data_provider = DatabaseReader(connection_string)
        else:
        """
        # Default to JSON file provider
        self.data_provider = JsonFileLoader(data_dir)
        self._load_data()
        

    
    def _load_data(self):
        """Load all data using the configured data provider."""
        logger.info("Loading inventory data from data provider")
        self.communities = self.data_provider.load_communities()
        self.units = self.data_provider.load_units()
        self.pet_policies = self.data_provider.load_pet_policies()
        self.specials = self.data_provider.load_specials()
        logger.info(f"Loaded data: {len(self.communities)} communities, {sum(len(units) for units in self.units.values())} total units")
    
    def reload_data(self):
        """Reload data using the configured data provider."""
        self._load_data()
    
    @classmethod
    def from_json_files(cls, data_dir: str = None) -> 'InventoryService':
        """Create inventory service using JSON file loader."""
        return cls(data_provider=JsonFileLoader(data_dir))
    
    @classmethod
    def from_database(cls, connection_string: str) -> 'InventoryService':
        """Create inventory service using database reader (placeholder)."""
        return cls(data_provider=DatabaseReader(connection_string))
    
    def get_available_units(self, community_id: str, bedrooms: int) -> List[Dict[str, Any]]:
        """Get available units for a community with specified bedroom count."""
        logger.info(f"Searching for available units: community_id={community_id}, bedrooms={bedrooms}")
        
        if community_id not in self.units:
            logger.warning(f"Community {community_id} not found in inventory")
            return []
        
        units = self.units[community_id]
        available = [
            unit for unit in units 
            if unit["available"] and unit["bedrooms"] == bedrooms
        ]
        
        logger.info(f"Found {len(available)} available {bedrooms}-bedroom units in {community_id}")
        return available

    def get_pet_policy(self, community_id: str, pet_type: str) -> Dict[str, Any]:
        """Get pet policy for a community and pet type."""
        logger.info(f"Looking up pet policy: community_id={community_id}, pet_type={pet_type}")
        
        if community_id not in self.pet_policies:
            logger.warning(f"Pet policies not found for community {community_id}")
            return {"allowed": False, "notes": "Community not found"}
        
        policies = self.pet_policies[community_id]
        if pet_type not in policies:
            logger.warning(f"Pet policy for {pet_type} not defined in {community_id}")
            return {"allowed": False, "notes": f"Policy for {pet_type} not defined"}
        
        policy = policies[pet_type]
        logger.info(f"Found pet policy for {pet_type} in {community_id}: allowed={policy.get('allowed', False)}")
        return policy

    def get_pricing(self, community_id: str, unit_id: str, move_in_date: str) -> Optional[Dict[str, Any]]:
        """Get pricing information for a specific unit and move-in date."""
        logger.info(f"Getting pricing: community_id={community_id}, unit_id={unit_id}, move_in_date={move_in_date}")
        
        if community_id not in self.units:
            logger.warning(f"Community {community_id} not found for pricing lookup")
            return None
        
        unit = None
        for u in self.units[community_id]:
            if u["unit_id"] == unit_id:
                unit = u
                break
        
        if not unit:
            logger.warning(f"Unit {unit_id} not found in community {community_id}")
            return None
        
        # Calculate pricing with potential specials
        base_rent = unit["base_rent"]
        effective_rent = base_rent
        applied_specials = []
        
        # Apply move-in date based specials
        move_in = datetime.strptime(move_in_date, "%Y-%m-%d")
        logger.info(f"Calculating specials for move-in date: {move_in_date} (month: {move_in.month})")
        
        # Summer special (June-August move-ins)
        if 6 <= move_in.month <= 8:
            summer_special = next((s for s in self.specials if s["name"] == "Summer Special"), None)
            if summer_special:
                discount = base_rent * (summer_special["amount"] / 100)
                effective_rent -= discount
                applied_specials.append({
                    "name": summer_special["name"],
                    "discount": discount,
                    "type": "monthly_discount"
                })
                logger.info(f"Applied Summer Special: ${discount:.2f} discount")
        
        # Random chance for other specials
        if random.random() < 0.3:  # 30% chance
            other_specials = [s for s in self.specials if s["name"] != "Summer Special"]
            if other_specials:  # Only if there are other specials available
                special = random.choice(other_specials)
                logger.info(f"Randomly selected additional special: {special['name']}")
                if special["discount_type"] == "first_month_free":
                    applied_specials.append({
                        "name": special["name"],
                        "discount": base_rent,
                        "type": "first_month_free"
                    })
                    logger.info(f"Applied {special['name']}: First month free (${base_rent:.2f})")
                elif special["discount_type"] == "flat_discount":
                    applied_specials.append({
                        "name": special["name"], 
                        "discount": special["amount"],
                        "type": "move_in_credit"
                    })
                    logger.info(f"Applied {special['name']}: ${special['amount']:.2f} move-in credit")
        
        total_discount = sum(special["discount"] for special in applied_specials)
        logger.info(f"Pricing calculated for {unit_id}: base_rent=${base_rent:.2f}, effective_rent=${effective_rent:.2f}, total_discounts=${total_discount:.2f}, specials_count={len(applied_specials)}")
        
        return {
            "community_id": community_id,
            "unit_id": unit_id,
            "unit_details": unit,
            "move_in_date": move_in_date,
            "pricing": {
                "base_rent": base_rent,
                "effective_rent": effective_rent,
                "security_deposit": base_rent,  # Typically one month's rent
                "application_fee": 75,
                "admin_fee": 150
            },
            "specials": applied_specials,
            "lease_terms": [6, 12, 15],  # Available lease lengths in months
            "available_date": unit["available_date"]
        }
    
    def get_community_info(self, community_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific community."""
        return self.communities.get(community_id)
    
    def list_communities(self) -> List[str]:
        """Get list of all available community IDs."""
        return list(self.communities.keys())
    
    def get_units_by_community(self, community_id: str) -> List[Dict[str, Any]]:
        """Get all units for a specific community."""
        return self.units.get(community_id, [])
    
    def get_available_specials(self) -> List[Dict[str, Any]]:
        """Get list of all available specials."""
        return self.specials.copy()