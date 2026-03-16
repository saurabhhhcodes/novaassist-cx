import boto3
import os
import decimal
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv() # Load credentials from .env

def setup_infrastructure():
    region = os.getenv("AWS_REGION", "us-east-1")
    s3 = boto3.client("s3", region_name=region)
    dynamodb = boto3.resource("dynamodb", region_name=region)
    
    # 1. S3 Bucket
    bucket_name = os.getenv("S3_BUCKET_NAME", "novaassist-cx-screenshots")
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists.")
        elif e.response['Error']['Code'] == 'BucketAlreadyExists':
             print(f"Bucket {bucket_name} already exists globally.")
        else:
            print(f"Error creating bucket: {e}")

    # 2. Conversations Table
    chats_table_name = os.getenv("DYNAMODB_CHATS_TABLE", "Conversations")
    try:
        table = dynamodb.create_table(
            TableName=chats_table_name,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"Creating table {chats_table_name}...")
        table.wait_until_exists()
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            print(f"Error creating {chats_table_name}: {e}")

    # 3. Orders Table
    orders_table_name = os.getenv("DYNAMODB_ORDERS_TABLE", "EnterpriseOrders")
    try:
        table = dynamodb.create_table(
            TableName=orders_table_name,
            KeySchema=[{'AttributeName': 'order_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'order_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"Creating table {orders_table_name}...")
        table.wait_until_exists()
        
        # Seed experimental orders
        seed_orders = [
            {'order_id': 'ORD-4421', 'customer_email': 'saurabh@exclusive.com', 'status': 'SHIPPED', 'items': ['MacBook Pro M3 Max', 'LG 38" UltraWide'], 'total_amount': 5498.00, 'shipping_address': '456 Tech Park, Whitefield, Bangalore', 'tracking_number': 'NS-9921004512', 'estimated_delivery': '2026-03-20', 'issue_history': []},
            {'order_id': 'ORD-8812', 'customer_email': 'saurabh@exclusive.com', 'status': 'PROCESSING', 'items': ['NVIDIA RTX 4090', 'ASUS ROG Z790'], 'total_amount': 2150.00, 'shipping_address': '789 Silicon Valley, Palo Alto, CA', 'tracking_number': 'TBD', 'estimated_delivery': '2026-03-25', 'issue_history': []},
            {'order_id': 'ORD-777', 'customer_email': 'saurabh@exclusive.com', 'status': 'SHIPPED', 'items': ['Custom Liquid-Cooled AI Workstation'], 'total_amount': 4200.00, 'shipping_address': 'Flat 402, Elite Meadows, Bangalore', 'tracking_number': 'NS-7770001234', 'estimated_delivery': '2026-03-18', 'issue_history': []}
        ]
        with table.batch_writer() as batch:
            for order in seed_orders:
                order['total_amount'] = decimal.Decimal(str(order['total_amount']))
                batch.put_item(Item=order)
        print(f"Seed data inserted into {orders_table_name}.")
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            print(f"Error creating {orders_table_name}: {e}")

if __name__ == "__main__":
    setup_infrastructure()
