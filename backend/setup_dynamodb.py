import boto3
import os
from botocore.exceptions import ClientError

def create_nova_tables():
    region = os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    
    # SupportTickets Table
    tickets_table_name = os.getenv("DYNAMODB_TICKETS_TABLE", "SupportTickets")
    try:
        table = dynamodb.create_table(
            TableName=tickets_table_name,
            KeySchema=[
                {'AttributeName': 'ticket_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'ticket_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {tickets_table_name}...")
        table.wait_until_exists()
        print(f"Table {tickets_table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {tickets_table_name} already exists.")
        else:
            print(f"Error creating {tickets_table_name}: {e}")

    # Customers Table
    customers_table_name = os.getenv("DYNAMODB_CUSTOMERS_TABLE", "Customers")
    try:
        table = dynamodb.create_table(
            TableName=customers_table_name,
            KeySchema=[
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {customers_table_name}...")
        table.wait_until_exists()
        print(f"Table {customers_table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {customers_table_name} already exists.")
        else:
            print(f"Error creating {customers_table_name}: {e}")

if __name__ == "__main__":
    create_nova_tables()
