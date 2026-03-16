import os
import sys

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adapters.order_adapter import SqliteOrderAdapter
from memory_service import MemoryService

def reset_database():
    # 1. Reset Orders DB
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nova_enterprise.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")

    SqliteOrderAdapter(db_path=db_path)
    print("Database reset and seeded via Adapter.")

    # 2. Reset Session History (Clear memory)
    memory = MemoryService()
    demo_sessions = ["saurabh@exclusive.com", "jane.doe@enterprise.io"]
    for sid in demo_sessions:
        memory.clear_history(sid)
    
    print("Session history purged for demo users.")

if __name__ == "__main__":
    reset_database()
