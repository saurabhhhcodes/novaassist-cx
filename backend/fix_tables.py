import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def fix_conversations_table():
    region = os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table_name = os.getenv("DYNAMODB_CHATS_TABLE", "Conversations")
    
    # 1. Delete if exists
    try:
        table = dynamodb.Table(table_name)
        table.delete()
        print(f"Deleting table {table_name}...")
        table.wait_until_not_exists()
        print(f"Table {table_name} deleted.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Table {table_name} does not exist.")
        else:
            print(f"Error deleting table: {e}")

    # 2. Create with HASH only
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {table_name}...")
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except ClientError as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    fix_conversations_table()
