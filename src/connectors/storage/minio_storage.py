from logging import getLogger
from typing import Any
import pendulum
import io
import json

from common.infra.s3_client import get_s3_client

logger = getLogger(__name__)

class MinioStore: 

    def __init__(self, bucket: str = "bronze") -> None: 

        self._bucket = bucket

    @staticmethod
    def _build_object_key(source: str, file_name: str, partition: str, run_date: pendulum.DateTime | None, extension: str) -> str: 

        date_info = run_date.date() if run_date else "all"

        return f"{source}/{partition}/date={date_info}/{file_name}.{extension}"

    def put_json(
        self, 
        payload: dict[str, str], 
        source: str, 
        file_name: str, 
        partition: str, 
        run_date: pendulum.DateTime | None = None, 
        extension: str = "json"
    ) -> str: 

        minio_key = self._build_object_key(source, file_name, partition, run_date, extension)

        logger.info("Uploading '%s' to bucket '%s'", minio_key, self._bucket)
        data = json.dumps(payload).encode("utf-8")

        s3_client = get_s3_client()

        s3_client.put_object(
            Bucket = self._bucket,
            Key = minio_key,
            Body = io.BytesIO(data),
            ContentType="application/json"
        )

        return minio_key


    def get_json(self, key: str) -> dict[str, Any]: 

        logger.info("Pulling '%s' from bucket '%s'", key, self._bucket)

        s3_client = get_s3_client()

        response = s3_client.get_object(
            Bucket = self._bucket, 
            Key = key
        )

        content = response["Body"].read()
        payload = json.loads(content)

        return payload