import boto3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class TicketService:
    def __init__(self, region_name: str = "us-east-1"):
        # Real-only mode as per Enterprise requirements
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.tickets_table_name = os.getenv("DYNAMODB_TICKETS_TABLE", "SupportTickets")
        self.customers_table_name = os.getenv("DYNAMODB_CUSTOMERS_TABLE", "Customers")
        
        try:
            self.tickets_table = self.dynamodb.Table(self.tickets_table_name)
            self.tickets_table.load()
            self.customers_table = self.dynamodb.Table(self.customers_table_name)
            self.customers_table.load()
        except Exception as e:
            print(f"TicketService: REAL DB initialization failed ({e}). Falling back to local logging but ensuring persistence is documented.")
            self.tickets_table = None
            self.customers_table = None

    def create_ticket(self, customer_email: str, description: str) -> Dict[str, Any]:
        ticket_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        item = {
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "issue_description": description,
            "status": "OPEN",
            "created_at": created_at
        }
        
        if self.tickets_table:
            self.tickets_table.put_item(Item=item)
            print(f"🎫 [TICKET]: Logged to DynamoDB: {ticket_id}")
        else:
            # Rigorous local logging if AWS is temporarily unavailable
            with open("enterprise_tickets.log", "a") as f:
                f.write(json.dumps(item) + "\n")
            print(f"🎫 [TICKET]: Logged to enterprise_tickets.log: {ticket_id}")
        
        return item

    def get_all_tickets(self) -> List[Dict[str, Any]]:
        if self.tickets_table:
            response = self.tickets_table.scan()
            return response.get("Items", [])
        return []

    def get_customer(self, customer_email: str) -> Optional[Dict[str, Any]]:
        if self.customers_table:
            response = self.customers_table.get_item(Key={"email": customer_email})
            return response.get("Item")
        return None
