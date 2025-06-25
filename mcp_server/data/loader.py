"""
JSON data loader for apartment inventory data.
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path

class DataLoader:
    """Loads apartment data from JSON files."""
    
    def __init__(self, data_dir: str = None):
        """Initialize data loader with optional custom data directory."""
        if data_dir is None:
            self.data_dir = Path(__file__).parent
        else:
            self.data_dir = Path(data_dir)
    
    def load_communities(self) -> Dict[str, Any]:
        """Load community data from JSON file."""
        return self._load_json_file("communities.json")
    
    def load_units(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load unit data from JSON file."""
        return self._load_json_file("units.json")
    
    def load_pet_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load pet policy data from JSON file."""
        return self._load_json_file("pet_policies.json")
    
    def load_specials(self) -> List[Dict[str, Any]]:
        """Load special offers data from JSON file."""
        return self._load_json_file("specials.json")
    
    def _load_json_file(self, filename: str) -> Any:
        """Load and parse a JSON file."""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading {filename}: {e}")
    
    def reload_all_data(self) -> Dict[str, Any]:
        """Reload all data files and return as a single dictionary."""
        return {
            'communities': self.load_communities(),
            'units': self.load_units(),
            'pet_policies': self.load_pet_policies(),
            'specials': self.load_specials()
        }