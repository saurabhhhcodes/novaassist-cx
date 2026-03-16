import asyncio
import json
from backend.agent_brain import AgentBrain
from backend.nova_client import NovaClient

async def debug_agent():
    nova = NovaClient()
    brain = AgentBrain(nova)
    
    print("Testing execute_tool for update_order_status...")
    try:
        res = await brain.execute_tool("update_order_status", {"order_id": "ORD-777", "status": "SHIPPED"})
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error in update_order_status: {e}")

    print("\nTesting execute_tool for get_order_details...")
    try:
        res = await brain.execute_tool("get_order_details", {"order_id": "ORD-777"})
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error in get_order_details: {e}")

if __name__ == "__main__":
    asyncio.run(debug_agent())
