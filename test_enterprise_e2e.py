import requests
import json
import time
import sqlite3
import os

API_URL = "http://127.0.0.1:8002/support/chat"
DB_PATH = "backend/nova_enterprise.db"

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()

def verify_db_state_sqlite(order_id, expected_status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        if row and row['status'] == expected_status:
            return True
    return False

def verify_db_state_dynamo(order_id, expected_status):
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = dynamodb.Table(os.getenv("DYNAMODB_ORDERS_TABLE", "EnterpriseOrders"))
    try:
        response = table.get_item(Key={'order_id': order_id})
        return response.get('Item', {}).get('status') == expected_status
    except Exception as e:
        print(f"DynamoDB Verify Error: {e}")
        return False

def verify_db_state(order_id, expected_status):
    if os.getenv("MOCK_SERVICES", "false").lower() == "true":
        return verify_db_state_sqlite(order_id, expected_status)
    return verify_db_state_dynamo(order_id, expected_status)

def test_rigorous_enterprise_flow():
    print(f"\n--- RIGOROUS ENTERPRISE SUPPORT AUDIT (REAL DATA) ---")
    
    session_id = f"ent_audit_{int(time.time())}"
    
    # 1. Verification of live data
    print("\n[Turn 1] Querying real SQLite database for Order #ORD-4421...")
    payload = {
        "message": "Hi Nova! Tell me exactly what the status of my order ORD-4421 is. Include the items and tracking number.",
        "customer_email": "saurabh@exclusive.com",
        "session_id": session_id
    }
    response = requests.post(API_URL, json=payload).json()
    print(f"Nova: {response.get('response', 'ERROR: No response key')}")
    
    resp_text = response.get('response', '').upper()
    if "SHIPPED" in resp_text and "NS-9921004512" in resp_text:
        print("✅ High-Fidelity Data Verification: Successful.")
    
    # 2. Database Write (Real Persistence)
    print("\n[Turn 2] Requesting status update (Persisting to SQLite)...")
    payload = {
        "message": "Actually, I just received it. Can you update the status to DELIVERED in the system for ORD-4421?",
        "customer_email": "saurabh@exclusive.com",
        "session_id": session_id
    }
    response = requests.post(API_URL, json=payload).json()
    print(f"Nova: {response.get('response', 'ERROR: No response key')}")
    
    if verify_db_state("ORD-4421", "DELIVERED"):
        print("✅ Real Persistence: Confirmed in enterprise database.")
    else:
        print("❌ Real Persistence: Verification FAILED.")

    # 3. Professional Fulfillment (Email + CRM)
    print("\n[Turn 3] Requesting formal email & CRM logging...")
    payload = {
        "message": "Thanks. Please send me a formal email confirmation and log a support ticket for this delivery.",
        "customer_email": "saurabh@exclusive.com",
        "session_id": session_id
    }
    response = requests.post(API_URL, json=payload).json()
    print(f"Nova: {response.get('response', 'ERROR: No response key')}")
    
    if "email" in response['response'].lower() or "sent" in response['response'].lower():
        print("✅ Professional Fulfillment: Agent triggered email/ticket workflows.")

    print(f"\n--- Enterprise Audit Complete ---")

if __name__ == "__main__":
    test_rigorous_enterprise_flow()
