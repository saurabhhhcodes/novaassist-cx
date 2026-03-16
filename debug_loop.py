import asyncio
import json
import traceback
import os
from backend.agent_brain import AgentBrain
from backend.nova_client import NovaClient

async def debug_full_loop():
    # Set mock mode to False to test real Bedrock logic
    os.environ["MOCK_SERVICES"] = "false"
    nova = NovaClient()
    brain = AgentBrain(nova)
    
    print("\n--- FAILING TURN DEBUG ---")
    session_id = f"debug_session_{int(time.time())}" if 'time' in globals() else "debug_session_123"
    import time
    session_id = f"debug_session_{int(time.time())}"
    
    user_input = "Hi Nova! I'm Saurabh. Can you tell me the status of my order #ORD-777?"
    
    try:
        result = await brain.run_agent_loop(session_id, user_input)
        print(f"Result: {result['response']}")
    except Exception:
        print("\n❌ CAUGHT TOP-LEVEL EXCEPTION:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_full_loop())
