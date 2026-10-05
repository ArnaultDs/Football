import boto3

from common.settings import settings

s3_client = boto3.client(
    's3', 
    endpoint_url = settings.minio_endpoint_url,
    aws_access_key_id = settings.minio_pipeline_access_key,
    aws_secret_access_key = settings.minio_pipeline_secret_key
)