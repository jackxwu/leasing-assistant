"""
Vector similarity search for pet policy matching using FAISS.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    logger.warning("FAISS or sentence-transformers not available. Vector search disabled.")
    VECTOR_SEARCH_AVAILABLE = False

class PetPolicyVectorSearch:
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize vector search for pet policies.
        
        Args:
            confidence_threshold: Minimum confidence score for matches (0.0-1.0)
        """
        if not VECTOR_SEARCH_AVAILABLE:
            logger.warning("Vector search dependencies not available")
            self.enabled = False
            return
            
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.index = None
        self.pet_types = []
        self.cache = {}
        self.enabled = True
        
        # Try to load model
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Vector search model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load vector search model: {e}")
            self.enabled = False
    
    def build_index(self, pet_types: List[str]) -> bool:
        """
        Build FAISS index from pet types.
        
        Args:
            pet_types: List of pet type strings from JSON data
            
        Returns:
            True if index built successfully, False otherwise
        """
        if not self.enabled or not pet_types:
            return False
            
        try:
            logger.info(f"Building vector index for pet types: {pet_types}")
            
            # Generate embeddings for pet types
            embeddings = self.model.encode(pet_types)
            
            # Create FAISS index (Inner Product for cosine similarity)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            self.pet_types = pet_types
            logger.info(f"Vector index built successfully with {len(pet_types)} pet types")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")
            self.enabled = False
            return False
    
    def find_best_match(self, query: str) -> Tuple[Optional[str], float]:
        """
        Find best matching pet type using vector similarity.
        
        Args:
            query: User's pet type query
            
        Returns:
            Tuple of (matched_pet_type, confidence_score)
            Returns (None, score) if no good match found
        """
        if not self.enabled or self.index is None:
            return None, 0.0
        
        # Check cache first
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Encode query
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search for best match
            scores, indices = self.index.search(query_embedding.astype('float32'), k=1)
            
            best_score = float(scores[0][0])
            best_match_idx = indices[0][0]
            
            if best_score >= self.confidence_threshold:
                matched_type = self.pet_types[best_match_idx]
                result = (matched_type, best_score)
            else:
                result = (None, best_score)
            
            # Cache result
            self.cache[cache_key] = result
            
            logger.info(f"Vector search: '{query}' -> '{result[0]}' (confidence: {result[1]:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Vector search failed for '{query}': {e}")
            return None, 0.0
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Updated confidence threshold to {self.confidence_threshold}")
    
    def clear_cache(self):
        """Clear the search cache."""
        self.cache.clear()
        logger.info("Vector search cache cleared")
    
    def get_stats(self) -> Dict:
        """Get search statistics."""
        return {
            "enabled": self.enabled,
            "confidence_threshold": self.confidence_threshold,
            "indexed_types": len(self.pet_types) if self.pet_types else 0,
            "cache_size": len(self.cache)
        }