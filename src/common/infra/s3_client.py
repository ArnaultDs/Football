from __future__ import annotations
from functools import cache

import boto3

from common.config import get_settings

@cache
def get_s3_client(): 
    settings = get_settings()
    return boto3.client(
        's3', 
        endpoint_url=settings.minio_endpoint_url,
        aws_access_key_id=settings.minio_pipeline_access_key,
        aws_secret_access_key=settings.minio_pipeline_secret_key
    )