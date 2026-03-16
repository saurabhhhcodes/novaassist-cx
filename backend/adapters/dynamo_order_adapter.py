import boto3
import os
import decimal
from typing import Dict, Any, List, Optional
from .base_adapter import BaseDataAdapter

class DynamoDBOrderAdapter(BaseDataAdapter):
    def __init__(self, region_name: str = "us-east-1"):
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table_name = os.getenv("DYNAMODB_ORDERS_TABLE", "EnterpriseOrders")
        self.table = self.dynamodb.Table(self.table_name)

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key={'order_id': record_id})
            if 'Item' in response:
                item = response['Item']
                # Convert Decimals back to floats/ints for JSON serialization
                return self._convert_decimals(item)
        except Exception as e:
            print(f"DynamoDBOrderAdapter: Error fetching {record_id} ({e})")
        return None

    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        if not updates:
            return False
        
        update_expression = "SET "
        expression_values = {}
        expression_names = {}
        
        for k, v in updates.items():
            if isinstance(v, float):
                v = decimal.Decimal(str(v))
            
            # Use placeholder for attribute names to avoid reserved keyword issues
            placeholder = f"#{k}"
            val_placeholder = f":{k}"
            
            update_expression += f"{placeholder} = {val_placeholder}, "
            expression_names[placeholder] = k
            expression_values[val_placeholder] = v
            
        update_expression = update_expression.rstrip(", ")
        
        try:
            self.table.update_item(
                Key={'order_id': record_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values
            )
            return True
        except Exception as e:
            print(f"DynamoDBOrderAdapter: Error updating {record_id} ({e})")
            return False

    def list_records(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            # Simple scan for demo purposes
            response = self.table.scan()
            items = response.get('Items', [])
            return [self._convert_decimals(i) for i in items]
        except Exception as e:
            print(f"DynamoDBOrderAdapter: Error scanning orders ({e})")
            return []

    def _convert_decimals(self, obj):
        if isinstance(obj, list):
            return [self._convert_decimals(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, decimal.Decimal):
            return float(obj) if obj % 1 > 0 else int(obj)
        return obj
