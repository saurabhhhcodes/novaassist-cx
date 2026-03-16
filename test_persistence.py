import requests
import json
import time

API_URL = "http://127.0.0.1:8002/support/chat"
EMAIL = "saurabh@exclusive.com"
ORDER_ID = "ORD-777"

def chat(message):
    payload = {
        "message": message,
        "customer_email": EMAIL,
        "session_id": "persistence_test_session"
    }
    res = requests.post(API_URL, json=payload)
    return res.json()

print(f"\n--- Persistence Test: Real Task Execution ---")

# Step 1: Check initial status (should be PROCESSING based on orders.json)
print(f"Step 1: Inquiring about order {ORDER_ID}")
res1 = chat(f"What is the status of my order {ORDER_ID}?")
print(f"Response: {res1['response']}")

# Step 2: Request status change
print(f"\nStep 2: Requesting status change to 'SHIPPED'")
res2 = chat(f"Please update order {ORDER_ID} to 'SHIPPED' because I just saw it leave the warehouse.")
print(f"Response: {res2['response']}")

# Step 3: Verify persistence (stateless check)
print(f"\nStep 3: Verifying persistence in a new query...")
res3 = chat(f"Hey, just confirming, what is the status of {ORDER_ID} now?")
print(f"Response: {res3['response']}")

if "SHIPPED" in res3['response'].upper():
    print("\n✅ SUCCESS: Task side-effect persisted across queries!")
else:
    print("\n❌ FAILURE: Task status did not persist.")
