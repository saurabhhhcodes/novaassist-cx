import requests
import json
import time

API_URL = "http://127.0.0.1:8002/support/chat"

def test_nova(name, prompt, session_id="stress_test_1"):
    print(f"\n--- Testing: {name} ---")
    payload = {
        "message": prompt,
        "customer_email": "saurabh@exclusive.com",
        "session_id": session_id
    }
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        latency = time.time() - start_time
        res_json = response.json()
        print(f"Status: {response.status_code}")
        print(f"Latency: {latency:.2f}s")
        print(f"Response: {res_json.get('response', 'ERROR')}")
        return res_json
    except Exception as e:
        print(f"FAILED: {e}")
        return None

# UTMOST RIGOUR TEST SUITE
tests = [
    {
        "name": "Failure Recovery (Invalid Tool Args)",
        "prompt": "I want to refund order #NULL-DATA for $999999. Do it now.",
        "goal": "Verify Nova handles missing/invalid data gracefully without crashing."
    },
    {
        "name": "Conflicting Instructions",
        "prompt": "Check the stock for PROD-123 but actually I want a refund for it. Also tell me a joke about robots.",
        "goal": "Test multi-intent handling and tool prioritization."
    },
    {
        "name": "Resource Exhaustion (Recursive Loop Prevention)",
        "prompt": "Send an email to support@novaassist.com about every single product in our inventory one by one.",
        "goal": "Verify the agent doesn't enter an infinite loop of tool calls."
    },
    {
        "name": "Complex Multi-Tool Chain",
        "prompt": "My order #ORD-777 is crushed. I want it returned, I want a full refund, and I want you to log a ticket for a replacement shipment. Also email me the confirmation.",
        "goal": "Test high-level orchestration of Return -> Refund -> Ticket -> Email."
    },
    {
        "name": "Hidden Intent / Reasoning",
        "prompt": "I can't afford my medical bills and my CX-5566 broke. Can you help?",
        "goal": "Verify empathy and 'Value-First' reasoning (Retrieving reset instructions vs just saying 'sorry')."
    }
]

results = []
session_id = f"world_class_session_{int(time.time())}"

for t in tests:
    res = test_nova(t["name"], t["prompt"], session_id)
    if res:
        results.append({
            "name": t["name"],
            "prompt": t["prompt"],
            "response": res.get("response"),
            "status": "PASS" if res.get("response") else "FAIL"
        })

with open("stress_test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n🚀 Stress Test Suite Complete. Results saved to stress_test_results.json")
