import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def verify_bedrock():
    region = os.getenv("AWS_REGION", "us-east-1")
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    
    # Try a simple Nova Lite call
    model_id = "us.amazon.nova-lite-v1:0"
    
    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Hello, are you active?"}]}]
        )
        print("Bedrock Connectivity: SUCCESS")
        print(f"Response: {response['output']['message']['content'][0]['text']}")
    except Exception as e:
        print(f"Bedrock Connectivity: FAILED ({e})")

if __name__ == "__main__":
    verify_bedrock()
