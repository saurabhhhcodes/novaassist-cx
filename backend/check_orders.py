import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nova_enterprise.db")

def check_orders():
    if not os.path.exists(DB_PATH):
        print("Database not found. Run reset_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT order_id, customer_email, status, items, tracking_number FROM orders")
    rows = cursor.fetchall()

    print(f"{'Order ID':<10} | {'Email':<25} | {'Status':<12} | {'Items':<40} | {'Tracking'}")
    print("-" * 110)
    for row in rows:
        print(f"{row[0]:<10} | {row[1]:<25} | {row[2]:<12} | {row[3][:38]+'...' if len(row[3]) > 38 else row[3]:<40} | {row[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_orders()
