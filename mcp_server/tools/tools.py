"""
Domain tools for apartment leasing operations.

These are the three required domain tools that the LLM agent will orchestrate:
- check_availability: Check unit availability by community and bedroom count
- check_pet_policy: Check pet policies for specific communities and pet types  
- get_pricing: Get pricing information for units and move-in dates

Functions return structured data that can be used by the LLM to craft responses.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os
import logging

from data import InventoryService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize inventory service with JSON file loader (default)
inventory = InventoryService()


def check_availability(community_id: str, bedrooms: int) -> Dict[str, Any]:
    """
    Check apartment unit availability by community and bedroom count.
    
    Args:
        community_id: Community identifier (e.g., 'sunset-ridge')
        bedrooms: Number of bedrooms required (1-4)
        
    Returns:
        Dictionary containing availability information:
        {
            "unit_id": "12B",
            "description": "3 bed 2.5 bath corner unit",
            "sqft": 1400,
            "floor": 12,
            "available_date": "2025-07-15",
            "amenities": ["balcony", "city_view"],
            "available": true
        }
        
        Or if no units available:
        {
            "available": false,
            "message": "No 2-bedroom units available in sunset-ridge"
        }
    """
    logger.info(f"LLM called check_availability: community_id={community_id}, bedrooms={bedrooms}")
    
    available_units = inventory.get_available_units(community_id, bedrooms)
    
    if not available_units:
        logger.error("no available units")
        return {
            "available": False,
            "message": f"No {bedrooms}-bedroom units available in {community_id}",
            "units": []
        }
    
    return {
        "available": True,

        "count": len(available_units),
        "units": available_units,
        "community_id": community_id,
        "bedrooms": bedrooms
    }


def check_pet_policy(community_id: str, pet_type: str) -> Dict[str, Any]:
    """
    Check pet policy for a specific community and pet type.
    
    Args:
        community_id: Community identifier (e.g., 'sunset-ridge')
        pet_type: Type of pet ('cat', 'dog', 'bird', 'fish', 'small_pet')
        
    Returns:
        Dictionary containing pet policy information:
        {
            "allowed": true,
            "fee": 50,
            "deposit": 200,
            "monthly_rent": 25,
            "max_pets": 2,
            "weight_limit": 60,  # for dogs
            "restrictions": ["must be declawed"],
            "notes": "Max 2 pets per unit"
        }
        
        Or if pets not allowed:
        {
            "allowed": false,
            "notes": "Dogs not permitted due to building policy"
        }
    """
    logger.info(f"LLM called check_pet_policy: community_id={community_id}, pet_type={pet_type}")
    
    policy = inventory.get_pet_policy(community_id, pet_type)
    logger.info(f"inventory returend {policy}")
    
    return {
        "community_id": community_id,
        "pet_type": pet_type,
        "allowed": policy["allowed"],
        "fee": policy.get("fee", 0),
        "deposit": policy.get("deposit", 0),
        "monthly_rent": policy.get("monthly_rent", 0),
        "restrictions": policy.get("restrictions", []),
        "notes": policy.get("notes", "")
    }


def get_pricing(community_id: str, unit_id: str, move_in_date: str) -> Dict[str, Any]:
    """
    Get pricing information for a specific unit and move-in date.
    
    Args:
        community_id: Community identifier (e.g., 'sunset-ridge')
        unit_id: Unit identifier (e.g., '12B', 'A101')
        move_in_date: Desired move-in date in YYYY-MM-DD format
        
    Returns:
        Dictionary containing pricing information:
        {
            "rent": 2495,
            "security_deposit": 2495,
            "application_fee": 75,
            "admin_fee": 150,
            "special": "1st month free",
            "discount_amount": 2495,
            "effective_rent": 2495,
            "lease_terms": [6, 12, 15],
            "available_date": "2025-07-15"
        }
        
        Or if unit not found:
        {
            "error": "Unit 12B not found in sunset-ridge",
            "available": false
        }
    """
    logger.info(f"LLM called get_pricing: community_id={community_id}, unit_id={unit_id}, move_in_date={move_in_date}")
    
    pricing = inventory.get_pricing(community_id, unit_id, move_in_date)
    
    if not pricing:
        logger.error(f"no pricing")
        return {
            "error": f"Unit {unit_id} not found in {community_id}",
            "available": False
        }
    
    return pricing


# Helper functions for data validation and formatting

def validate_community_id(community_id: str) -> bool:
    """Validate that community_id exists and is properly formatted."""
    # TODO: Implement community validation
    pass


def validate_bedrooms(bedrooms: int) -> bool:
    """Validate bedroom count is within acceptable range."""
    return isinstance(bedrooms, int) and 1 <= bedrooms <= 4


def validate_pet_type(pet_type: str) -> bool:
    """Validate pet type is one of the accepted values."""
    valid_types = {'cat', 'dog', 'bird', 'fish', 'small_pet'}
    return pet_type.lower() in valid_types


def validate_move_in_date(move_in_date: str) -> bool:
    """Validate move-in date format and ensure it's not in the past."""
    try:
        date = datetime.strptime(move_in_date, '%Y-%m-%d')
        return date >= datetime.now().date()
    except ValueError:
        return False


def format_currency(amount: float) -> str:
    """Format currency amount for display."""
    return f"${amount:,.0f}"


def calculate_effective_rent(base_rent: float, specials: List[Dict[str, Any]]) -> float:
    """Calculate effective monthly rent after applying specials."""
    # TODO: Implement special calculation logic
    pass