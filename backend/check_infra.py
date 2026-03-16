import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def check_and_recreate():
    region = os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table_name = os.getenv("DYNAMODB_CHATS_TABLE", "Conversations")
    
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table {table_name} STILL EXISTS.")
        print(f"Schema: {table.key_schema}")
        # If it has RANGE key, we must delete it
        if len(table.key_schema) > 1:
            print("Deleting table with wrong schema...")
            table.delete()
            # No wait this time, just inform
            print("Deletion triggered. Please wait a moment.")
        else:
            print("Table has correct schema.")
            
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Table {table_name} does not exist. Creating now...")
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'session_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'session_id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            print("Creation triggered.")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_and_recreate()
