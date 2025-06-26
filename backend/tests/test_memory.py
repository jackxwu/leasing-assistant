#!/usr/bin/env python3
"""
Simple test script to verify agent memory functionality.
"""

import json

import requests

API_BASE_URL = "http://localhost:8000"

def test_memory_functionality():
    """Test that agent memory works correctly."""
    
    # Generate a test client ID
    client_id = "test_client_123"
    
    print(f"Testing memory functionality with client_id: {client_id}")
    
    # Test 1: First message
    print("\n=== Test 1: First message ===")
    request1 = {
        "lead": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "message": "Hi, I'm looking for a 2-bedroom apartment",
        "preferences": {
            "bedrooms": 2,
            "move_in": "2025-08-01"
        },
        "community_id": "sunset-ridge",
        "client_id": client_id
    }
    
    response1 = requests.post(f"{API_BASE_URL}/api/reply", json=request1)
    print(f"Response 1: {response1.json()['reply'][:100]}...")
    
    # Test 2: Follow-up message (should have memory of previous conversation)
    print("\n=== Test 2: Follow-up message ===")
    request2 = {
        "lead": {
            "name": "John Doe", 
            "email": "john@example.com"
        },
        "message": "Do you allow cats?",
        "community_id": "sunset-ridge",
        "client_id": client_id
    }
    
    response2 = requests.post(f"{API_BASE_URL}/api/reply", json=request2)
    print(f"Response 2: {response2.json()['reply'][:100]}...")
    
    # Test 3: Check memory stats
    print("\n=== Test 3: Memory stats ===")
    stats_response = requests.get(f"{API_BASE_URL}/api/memory/stats")
    stats = stats_response.json()
    print(f"Memory stats: {stats}")
    
    # Test 4: Different client ID (should not have memory of previous conversation)
    print("\n=== Test 4: Different client ===")
    different_client_id = "test_client_456"
    request3 = {
        "lead": {
            "name": "Jane Smith",
            "email": "jane@example.com"
        },
        "message": "What was I asking about before?",
        "community_id": "sunset-ridge",
        "client_id": different_client_id
    }
    
    response3 = requests.post(f"{API_BASE_URL}/api/reply", json=request3)
    print(f"Response 3: {response3.json()['reply'][:100]}...")
    
    # Test 5: Updated memory stats
    print("\n=== Test 5: Updated memory stats ===")
    stats_response2 = requests.get(f"{API_BASE_URL}/api/memory/stats")
    stats2 = stats_response2.json()
    print(f"Updated memory stats: {stats2}")
    
    # Test 6: Clear memory for first client
    print("\n=== Test 6: Clear memory ===")
    clear_response = requests.delete(f"{API_BASE_URL}/api/memory/{client_id}")
    print(f"Clear memory result: {clear_response.json()}")
    
    # Test 7: Final memory stats
    print("\n=== Test 7: Final memory stats ===")
    stats_response3 = requests.get(f"{API_BASE_URL}/api/memory/stats")
    stats3 = stats_response3.json()
    print(f"Final memory stats: {stats3}")

if __name__ == "__main__":
    try:
        test_memory_functionality()
        print("\n✅ Memory functionality test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")