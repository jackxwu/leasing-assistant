from pydantic import BaseModel
from typing import Optional
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

class ChatResponse(BaseModel):
    reply: str
    action: str  # "propose_tour", "ask_clarification", "handoff_human"
    proposed_time: Optional[datetime] = None