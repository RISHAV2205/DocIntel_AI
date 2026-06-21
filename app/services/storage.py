import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


def upload_file(file_bytes: bytes, filename: str, user_id: int) -> str:
    """
    Uploads file to S3.
    Returns the storage key — save this in DB instead of local file_path.
    """
    storage_key = f"documents/{user_id}/{filename}"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=storage_key,
        Body=file_bytes,
        ContentType=get_content_type(filename)
    )

    return storage_key


def download_file(storage_key: str) -> bytes:
    """
    Downloads file bytes from S3.
    Used in Celery task to fetch file for processing.
    """
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=storage_key)
    return response["Body"].read()


def delete_file(storage_key: str) -> None:
    """
    Deletes file from S3.
    """
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=storage_key)


def get_content_type(filename: str) -> str:
    extension = filename.rsplit(".", 1)[-1].lower()
    types = {
        "pdf": "application/pdf",
        "txt": "text/plain",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    return types.get(extension, "application/octet-stream")