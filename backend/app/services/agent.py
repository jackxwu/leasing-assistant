from app.models.schemas import ChatRequest, ChatResponse
from datetime import datetime, timedelta
import random

class AgentService:
    def __init__(self):
        self.available_units = [
            {"unit": "12B", "bedrooms": 2, "rent": 2400, "available_date": "2025-07-15"},
            {"unit": "8A", "bedrooms": 1, "rent": 1800, "available_date": "2025-06-30"},
            {"unit": "15C", "bedrooms": 3, "rent": 3200, "available_date": "2025-08-01"},
            {"unit": "4D", "bedrooms": 2, "rent": 2600, "available_date": "2025-07-01"},
        ]
        
        self.tour_times = [
            datetime.now() + timedelta(days=2, hours=10),
            datetime.now() + timedelta(days=2, hours=14),
            datetime.now() + timedelta(days=3, hours=11),
            datetime.now() + timedelta(days=4, hours=15),
            datetime.now() + timedelta(days=5, hours=13),
        ]
    
    def process_message(self, request: ChatRequest) -> ChatResponse:
        message_lower = request.message.lower()
        lead_name = request.lead.name.split()[0]  # First name only
        
        # Available units inquiry
        if any(word in message_lower for word in ["available", "vacancy", "open", "unit"]):
            if request.preferences and request.preferences.bedrooms:
                matching_units = [u for u in self.available_units if u["bedrooms"] == request.preferences.bedrooms]
            else:
                matching_units = self.available_units
            
            if matching_units:
                unit = random.choice(matching_units)
                pet_info = " Pets are welcome with a $200 deposit!" if "pet" in message_lower or "cat" in message_lower or "dog" in message_lower else ""
                tour_time = random.choice(self.tour_times)
                
                return ChatResponse(
                    reply=f"Hi {lead_name}! Great news - Unit {unit['unit']} ({unit['bedrooms']} bed) is available starting {unit['available_date']} for ${unit['rent']}/month.{pet_info} Would you like to schedule a tour? I have {tour_time.strftime('%A at %I:%M %p')} available.",
                    action="propose_tour",
                    proposed_time=tour_time
                )
        
        # Pricing inquiries
        elif any(word in message_lower for word in ["price", "rent", "cost", "expensive", "cheap", "budget"]):
            unit = random.choice(self.available_units)
            return ChatResponse(
                reply=f"Hi {lead_name}! Our {unit['bedrooms']}-bedroom units start at ${unit['rent']}/month. This includes water, trash, and access to our fitness center and pool. Would you like to see what's available in your budget range?",
                action="ask_clarification"
            )
        
        # Pet inquiries
        elif any(word in message_lower for word in ["pet", "cat", "dog", "animal"]):
            return ChatResponse(
                reply=f"Hi {lead_name}! We're pet-friendly! We welcome cats and dogs under 60lbs with a $200 pet deposit and $50/month pet rent. We even have an on-site dog park. Would you like to schedule a tour to see our pet amenities?",
                action="propose_tour",
                proposed_time=random.choice(self.tour_times)
            )
        
        # Amenity inquiries
        elif any(word in message_lower for word in ["amenities", "pool", "gym", "parking", "laundry"]):
            return ChatResponse(
                reply=f"Hi {lead_name}! We have amazing amenities including a resort-style pool, 24/7 fitness center, covered parking, in-unit laundry, and a resident lounge with co-working spaces. Want to see them in person?",
                action="propose_tour",
                proposed_time=random.choice(self.tour_times)
            )
        
        # Move-in date inquiries
        elif any(word in message_lower for word in ["move", "when", "date", "available"]):
            return ChatResponse(
                reply=f"Hi {lead_name}! We have units available starting as early as next month. When are you looking to move in? This will help me show you the best options.",
                action="ask_clarification"
            )
        
        # Application/lease inquiries
        elif any(word in message_lower for word in ["apply", "application", "lease", "qualify", "requirements"]):
            return ChatResponse(
                reply=f"Hi {lead_name}! Our application process is simple and can be completed online. We typically require 3x monthly rent in income and good rental history. I'd be happy to help you through the process - let me connect you with our leasing specialist.",
                action="handoff_human"
            )
        
        # Short/unclear messages
        elif len(message_lower.split()) < 3:
            return ChatResponse(
                reply=f"Hi {lead_name}! I'd love to help you find the perfect home. Could you tell me a bit more about what you're looking for? For example, how many bedrooms, your budget range, or when you'd like to move in?",
                action="ask_clarification"
            )
        
        # Default response for complex/unclear inquiries
        else:
            return ChatResponse(
                reply=f"Hi {lead_name}! Thanks for your interest in {request.community_id.replace('-', ' ').title()}! Your question is important to us - let me connect you with one of our leasing specialists who can give you detailed information and personalized assistance.",
                action="handoff_human"
            )