import boto3
from botocore.client import Config
from app.config import settings
import uuid
from fastapi import UploadFile

s3_client = boto3.client(
    's3',
    endpoint_url=settings.R2_ENDPOINT_URL,
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

async def upload_file(file: UploadFile, user_id: str) -> str:
    """Uploads file to R2 and returns key"""
    file_extension = file.filename.split(".")[-1]
    key = f"{user_id}/{uuid.uuid4()}.{file_extension}"
    
    s3_client.upload_fileobj(
        file.file,
        settings.R2_BUCKET_NAME,
        key,
        ExtraArgs={'ContentType': file.content_type}
    )
    return key

def generate_presigned_url(key: str) -> str:
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key},
        ExpiresIn=3600
    )
    return url
