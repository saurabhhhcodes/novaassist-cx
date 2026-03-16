import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from .base_adapter import BaseDataAdapter

class SqliteOrderAdapter(BaseDataAdapter):
    """
    Real SQLite-based Order Database Adapter.
    Provides rigorous persistence and relational structure for Enterprise-grade Nova.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Rigorous pathing for Enterprise deployment
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "nova_enterprise.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    customer_email TEXT,
                    status TEXT,
                    items TEXT,
                    total_amount REAL,
                    shipping_address TEXT,
                    tracking_number TEXT,
                    estimated_delivery TEXT,
                    issue_history TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Seed data if high-fidelity records are missing
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM orders WHERE order_id = 'ORD-4421'")
            if not cursor.fetchone():
                print("SqliteOrderAdapter: High-fidelity seed data missing. Seeding now...")
                seed_orders = [
                    ('ORD-4421', 'saurabh@exclusive.com', 'SHIPPED', '"MacBook Pro M3 Max, LG 38\\" UltraWide"', 5498.00, '456 Tech Park, Whitefield, Bangalore', 'NS-9921004512', '2026-03-20', '[]'),
                    ('ORD-8812', 'saurabh@exclusive.com', 'PROCESSING', '"NVIDIA RTX 4090, ASUS ROG Z790"', 2150.00, '789 Silicon Valley, Palo Alto, CA', 'TBD', '2026-03-25', '[]'),
                    ('ORD-777', 'saurabh@exclusive.com', 'SHIPPED', '"Custom Liquid-Cooled AI Workstation"', 4200.00, 'Flat 402, Elite Meadows, Bangalore', 'NS-7770001234', '2026-03-18', '[]')
                ]
                conn.executemany("INSERT OR REPLACE INTO orders (order_id, customer_email, status, items, total_amount, shipping_address, tracking_number, estimated_delivery, issue_history) VALUES (?,?,?,?,?,?,?,?,?)", seed_orders)
            conn.commit()

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM orders WHERE order_id = ?", (record_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                try:
                    data['items'] = json.loads(data['items'])
                except: pass
                try:
                    data['issue_history'] = json.loads(data['issue_history'])
                except: data['issue_history'] = []
                return data
        return None

    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        if not updates:
            return False
        
        set_clause = []
        params = []
        for k, v in updates.items():
            if k in ['items', 'issue_history']:
                v = json.dumps(v)
            set_clause.append(f"{k} = ?")
            params.append(v)
        
        params.append(record_id)
        query = f"UPDATE orders SET {', '.join(set_clause)} WHERE order_id = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    def list_records(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM orders"
        params = []
        if filters:
            where_clauses = []
            for k, v in filters.items():
                where_clauses.append(f"{k} = ?")
                params.append(v)
            query += " WHERE " + " AND ".join(where_clauses)
            
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for row in rows:
                data = dict(row)
                data['items'] = json.loads(data['items'])
                data['issue_history'] = json.loads(data['issue_history'])
                results.append(data)
            return results
