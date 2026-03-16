import boto3
import os
from botocore.exceptions import ClientError

class S3Utils:
    def __init__(self, region_name: str = "us-east-1"):
        self.mock_mode = os.getenv("MOCK_SERVICES", "true").lower() == "true"
        if self.mock_mode:
            self.s3 = None
            print("S3Utils: Running in MOCK MODE")
        else:
            self.s3 = boto3.client("s3", region_name=region_name)
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "novaassist-screenshots")

    def upload_file(self, file_bytes: bytes, file_name: str, content_type: str = "image/png") -> str:
        """
        Uploads a file to S3 and returns the public URL or S3 URI.
        """
        if self.mock_mode:
            return f"s3://mock-bucket/{file_name}"
            
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_bytes,
                ContentType=content_type
            )
            return f"s3://{self.bucket_name}/{file_name}"
        except Exception as e:
            print(f"S3 Upload Error: {e}")
            return f"local://{file_name}" # Fallback for local dev
