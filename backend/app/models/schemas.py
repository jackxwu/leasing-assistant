from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class Lead(BaseModel):
    name: str
    email: str

class Preferences(BaseModel):
    bedrooms: Optional[int] = None
    move_in: Optional[str] = None

class ChatRequest(BaseModel):
    lead: Lead
    message: str
    preferences: Optional[Preferences] = None
    community_id: str
    client_id: str

class ChatResponse(BaseModel):
    reply: str
    action: str  # "propose_tour", "ask_clarification", "handoff_human"
    proposed_time: Optional[str] = None  # ISO string format for frontend compatibility


class ClientPreferences(BaseModel):
    """
    Client preference model for learning and storing housing preferences over time.
    
    TODO: Confidence Decay - Implement time-based decay of confidence scores:
    - Preferences older than 30 days should have reduced confidence
    - Explicit mentions should decay slower than inferred preferences
    - Consider implementing exponential decay: confidence * exp(-days/decay_constant)
    """
    
    # Basic housing preferences
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    max_rent: Optional[int] = None
    move_in_date: Optional[str] = None

    # Location preferences
    preferred_communities: List[str] = Field(default_factory=list)
    floor_preferences: Optional[str] = None  # "high", "low", "ground", "any"

    # Pet information
    has_pets: Optional[bool] = None
    pet_types: List[str] = Field(default_factory=list)

    # Lifestyle preferences
    amenity_priorities: List[str] = Field(default_factory=list)  # "gym", "pool", "parking"
    noise_sensitivity: Optional[str] = None  # "high", "medium", "low"

    # Inferred preferences (learned from conversation)
    budget_conscious: Optional[bool] = None
    prefers_tours: Optional[bool] = None
    urgency_level: Optional[str] = None  # "urgent", "flexible", "browsing"

    # Metadata
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    source_messages: List[str] = Field(default_factory=list)  # Track which messages influenced prefs

