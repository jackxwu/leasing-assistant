"""
LLM-based preference extraction service for learning client preferences from conversation.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import anthropic
from app.models.schemas import ClientPreferences

logger = logging.getLogger(__name__)

class PreferenceExtractor:
    """Extract housing preferences from conversation using Claude."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"  # Fast, cheap model for extraction
    
    async def extract_preferences(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Extract preferences from a message using Claude.
        
        Args:
            message: The user message to analyze
            context: Optional context about the conversation
            
        Returns:
            Dictionary of extracted preferences with confidence indicators
        """
        try:
            prompt = self._create_extraction_prompt(message, context)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the JSON response
            response_text = response.content[0].text.strip()
            
            # Handle case where Claude wraps JSON in markdown
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            preferences = json.loads(response_text)
            
            logger.info(f"Extracted preferences from message: {preferences}")
            return preferences
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse preference extraction JSON: {e}")
            logger.error(f"Raw response: {response_text}")
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting preferences: {e}")
            return {}
    
    def _create_extraction_prompt(self, message: str, context: str) -> str:
        """Create the prompt for preference extraction."""
        
        prompt = f"""Extract housing preferences from this message. Return ONLY valid JSON.

Message: "{message}"
{f'Context: "{context}"' if context else ''}

Extract these preferences (only include if clearly mentioned):
- bedrooms (int): Number of bedrooms needed
- bathrooms (int): Number of bathrooms needed
- max_rent (int): Maximum rent budget in dollars
- min_sqft (int): Minimum square footage
- max_sqft (int): Maximum square footage
- move_in_date (string): Move-in date in YYYY-MM-DD format
- has_pets (bool): Whether they have pets
- pet_types (list): Types of pets (e.g., ["dog", "cat"])
- amenity_priorities (list): Important amenities (e.g., ["gym", "pool", "parking"])
- floor_preferences (string): "high", "low", "ground", or "any"
- budget_conscious (bool): If they mention budget concerns
- urgency_level (string): "urgent", "flexible", or "browsing"
- noise_sensitivity (string): "high", "medium", or "low"
- preferred_communities (list): Community names mentioned

Rules:
1. Only extract preferences that are CLEARLY stated
2. Don't infer unstated preferences
3. Return empty object {{}} if no clear preferences found
4. Use exact values mentioned (don't round numbers)
5. For pet_types, use singular forms: ["dog", "cat", "bird", "fish"]

Examples:
"I need a 2-bedroom apartment" → {{"bedrooms": 2}}
"My budget is $2500" → {{"max_rent": 2500}}
"I have a dog and cat" → {{"has_pets": true, "pet_types": ["dog", "cat"]}}
"I need to move ASAP" → {{"urgency_level": "urgent"}}
"No pets" → {{"has_pets": false}}
"I'm interested in Sunset Ridge" → {{"preferred_communities": ["Sunset Ridge"]}}
"Do you have units at Oak Valley Apartments?" → {{"preferred_communities": ["Oak Valley Apartments"]}}
"I need to move in July" → {{"move_in_date": "2025-07-01"}}
"Looking to move by March 15th" → {{"move_in_date": "2025-03-15"}}

Return JSON only:"""

        return prompt
    
    def update_preferences(self, current_prefs: ClientPreferences, 
                          extracted_prefs: Dict[str, Any], 
                          source_message: str) -> ClientPreferences:
        """
        Update client preferences with newly extracted preferences.
        
        Args:
            current_prefs: Current ClientPreferences object
            extracted_prefs: Dictionary of new preferences from extraction
            source_message: The message that generated these preferences
            
        Returns:
            Updated ClientPreferences object
        """
        if not extracted_prefs:
            return current_prefs
        
        # Create a copy to avoid mutating the original
        # Ensure current_prefs is a ClientPreferences object
        if isinstance(current_prefs, dict):
            current_prefs = ClientPreferences(**current_prefs)
        updated_prefs = current_prefs.model_copy(deep=True)
        
        # Update each extracted preference
        for key, value in extracted_prefs.items():
            if hasattr(updated_prefs, key) and value is not None:
                # Special handling for list fields
                if key in ["pet_types", "amenity_priorities", "preferred_communities"]:
                    current_list = getattr(updated_prefs, key) or []
                    if isinstance(value, list):
                        # Merge lists, avoiding duplicates
                        updated_list = list(set(current_list + value))
                        setattr(updated_prefs, key, updated_list)
                    elif isinstance(value, str):
                        # Single value to add to list
                        if value not in current_list:
                            current_list.append(value)
                            setattr(updated_prefs, key, current_list)
                else:
                    # Direct assignment for non-list fields
                    setattr(updated_prefs, key, value)
                
                # Set confidence based on explicitness
                confidence = self._calculate_confidence(key, value, source_message)
                updated_prefs.confidence_scores[key] = confidence
                
                logger.info(f"Updated preference {key}={value} with confidence {confidence:.2f}")
        
        # Update metadata
        if source_message not in updated_prefs.source_messages:
            updated_prefs.source_messages.append(source_message)
        updated_prefs.last_updated = datetime.now()
        
        return updated_prefs
    
    def _calculate_confidence(self, key: str, value: Any, message: str) -> float:
        """Calculate confidence score for a preference based on how it was mentioned."""
        
        message_lower = message.lower()
        
        # High confidence for explicit, specific mentions
        if key == "bedrooms" and ("bedroom" in message_lower or "bed" in message_lower):
            return 0.95
        elif key == "max_rent" and ("$" in message or "budget" in message_lower):
            return 0.90
        elif key == "has_pets" and any(word in message_lower for word in ["pet", "dog", "cat", "animal"]):
            return 0.95
        elif key == "urgency_level":
            if any(word in message_lower for word in ["asap", "urgent", "immediately", "soon"]):
                return 0.90
            elif any(word in message_lower for word in ["flexible", "no rush", "browsing"]):
                return 0.85
            else:
                return 0.70
        elif key == "move_in_date" and any(word in message_lower for word in ["move", "available", "date"]):
            return 0.85
        
        # Medium confidence for inferred preferences  
        elif key in ["budget_conscious", "noise_sensitivity"]:
            return 0.70
        
        # Default confidence for clear mentions
        return 0.80