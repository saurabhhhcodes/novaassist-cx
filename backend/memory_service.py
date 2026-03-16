import boto3
import os
import time
from typing import List, Dict, Any

class MemoryService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.table_name = os.getenv("DYNAMODB_CHATS_TABLE", "Conversations")
        self.table = self.dynamodb.Table(self.table_name)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        try:
            self.table.load()
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            print(f"Creating table {self.table_name}...")
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{'AttributeName': 'session_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'session_id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            ).wait_until_exists()

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            if 'Item' in response:
                return response['Item'].get('messages', [])
        except Exception as e:
            print(f"Error fetching history: {e}")
        return []

    def update_history(self, session_id: str, new_messages: List[Dict[str, Any]]):
        history = self.get_history(session_id)
        history.extend(new_messages)
        # Keep only last 20 messages to manage context window
        history = history[-20:]
        try:
            self.table.put_item(Item={
                'session_id': session_id,
                'messages': history,
                'updated_at': int(time.time())
            })
        except Exception as e:
            print(f"Error updating history: {e}")
    def clear_history(self, session_id: str):
        try:
            self.table.delete_item(Key={'session_id': session_id})
            print(f"Purged session history for {session_id}")
        except Exception as e:
            print(f"Error purging history: {e}")
