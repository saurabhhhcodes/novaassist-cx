import requests
import sys

def test_api():
    import os
    base_url = os.getenv("BASE_URL", "http://localhost:8002")
    print(f"Testing NovaAssist CX API at {base_url}...")
    
    try:
        # Test 1: Chat endpoint
        print("\nTest 1: Chat Endpoint (/support/chat)")
        payload = {
            "message": "Hello, I need help with my order.",
            "customer_email": "test@example.com"
        }
        # In a real run without valid Bedrock creds, this might fail or we'd mock it.
        # But for this test, let's see if the server is up.
        response = requests.post(f"{base_url}/support/chat", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Tickets endpoint
        print("\nTest 2: Tickets Endpoint (/tickets)")
        response = requests.get(f"{base_url}/tickets")
        print(f"Status: {response.status_code}")
        print(f"Tickets Found: {len(response.json())}")
        
        print("\nAPI Testing Completed.")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_api()
