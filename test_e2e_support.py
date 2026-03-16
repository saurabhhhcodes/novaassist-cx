import requests
import json
import time

API_URL = "http://127.0.0.1:8002/support/chat"
EMAIL = "saurabh@exclusive.com"

def test_e2e_support_flow():
    print(f"\n--- End-to-End Professional Support Audit ---")
    
    # Context: User is Gold tier, has a previous issue, and wants a status update + formal confirmation.
    queries = [
        "Hi Nova! I'm Saurabh. Can you tell me the status of my order #ORD-777? Also, I'm a bit worried because my last issue took a while to resolve.",
        "That's good to hear. Since it's still processing, can you send me a formal email confirmation of this status update? I need it for my records. Please make it professional."
    ]
    
    session_id = f"e2e_test_{int(time.time())}"
    
    for i, query in enumerate(queries):
        print(f"\n[Turn {i+1}] User: {query}")
        
        payload = {
            "message": query,
            "customer_email": EMAIL,
            "session_id": session_id
        }
        
        response = requests.post(API_URL, json=payload)
        res_json = response.json()
        
        print(f"Nova:\n{res_json['response']}")
        
        # Check for Thinking blocks
        if "<thinking>" in res_json['response']:
            print("✅ Reasoning: Thinking block detected.")
        
        # Check for tool execution logs (emitted in server console, but we can infer from response)
        if i == 1:
            if "Email" in res_json['response'] or "sent" in res_json['response'].lower():
                 print("✅ Action: Email tool execution inferred from response.")
            
            # Check for professionalism/loyalty mention
            if "Gold" in res_json['response']:
                print("✅ Personalization: Loyalty tier recognized and mentioned.")

    print(f"\n--- Audit Complete ---")

if __name__ == "__main__":
    test_e2e_support_flow()
