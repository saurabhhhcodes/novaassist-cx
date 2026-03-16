import requests
import json
import time

API_URL = "http://127.0.0.1:8002/support/chat"
EMAILS = ["test_user@example.com", "saurabh_test@example.com"]

def run_test_case(name, message, email=EMAILS[0]):
    print(f"\n--- [TEST CASE]: {name} ---")
    print(f"INPUT: {message}")
    
    start = time.time()
    try:
        response = requests.post(API_URL, json={
            "message": message,
            "customer_email": email
        })
        latency = time.time() - start
        
        if response.status_code == 200:
            res_data = response.json()
            print(f"STATUS: ✅ SUCCESS ({latency:.2f}s)")
            print(f"OUTPUT: {res_data['response']}")
            return {"name": name, "status": "PASS", "latency": f"{latency:.2f}s", "output": res_data['response']}
        else:
            print(f"STATUS: ❌ FAILED ({response.status_code})")
            return {"name": name, "status": "FAIL", "error": response.text}
    except Exception as e:
        print(f"STATUS: ❌ ERROR ({str(e)})")
        return {"name": name, "status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    results = []
    
    # 1. Identity & Memory
    results.append(run_test_case("Identity & Memory", "Hi, I am Saurabh. My order ID is #CX-1337. Remember this."))
    
    # 2. Context Retention (Follow-up)
    results.append(run_test_case("Context Retention", "Wait, what did I say my order ID was?", email=EMAILS[1])) # Testing specific session
    
    # 3. RAG - Refund Policy
    results.append(run_test_case("RAG - Refund Policy", "What is our 30-day refund policy for damaged products?"))
    
    # 4. RAG - Hardware Reset
    results.append(run_test_case("RAG - Reset Logic", "How can I reset my CX-5566 device safely?"))
    
    # 5. Agency - Update Order
    results.append(run_test_case("Agency - Update Order", "I am an admin. Update order #ORD-777 to 'DELIVERED'."))
    
    # 6. Agency - Process Refund
    results.append(run_test_case("Agency - Process Refund", "Process a $15 refund for #ORD-777 because the box was slightly crushed."))
    
    # 7. Agency - Inventory Check
    results.append(run_test_case("Agency - Inventory", "How many 'PROD-123' items do we have left?"))
    
    # 8. Multi-Step Agency (God Mode Lite)
    results.append(run_test_case("Multi-Step Reasoning", "Check inventory for CX-5566 and then email manager@axonflow.ai about the stock level."))

    # Write results to a file for the agent to read and format
    with open("/home/saurabh/.gemini/antigravity/scratch/novaassist-cx/test_audit_raw.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n\n✅ ALL TESTS COMPLETED. OUTPUT SAVED TO test_audit_raw.json")
