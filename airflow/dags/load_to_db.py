from airflow.sdk import dag, task
from typing import Any
from common.assets import raw_updated
import pendulum
from logging import getLogger

from db.control.manifest import ApiExtractionManifest
from db.control.manifest import DbtManifest
from connectors.storage.minio_storage import MinioConnector
from connectors.database.database_storage import DatabaseConnector



logger = getLogger(__name__)

@dag(schedule="0 * * * *", catchup=False)
def load_to_db(): 

    @task
    def get_pending_task() -> list[dict[str, Any]]: 
        return ApiExtractionManifest().claim_pending()

    @task 
    def load(task_to_load: dict[str, Any]) -> None: 
        
        path = task_to_load["location"]
        endpoint:str = task_to_load["endpoint"]
        api_extracted_at = task_to_load["api_extracted_at"]

        table_name = endpoint.replace("/", "_")

        try: 
            data = MinioConnector("bronze").read(path)
            DatabaseConnector().load(
                table_name=table_name,
                source_file=path,
                payload=data, 
                api_extracted_at=api_extracted_at
            )
        except Exception as e: 
            logger.error("An error has occured while loading to db: %s", str(e))
            ApiExtractionManifest().failed(path, str(e))
            return None

        ApiExtractionManifest().succeeded(path)
        DbtManifest().create(table_name, pendulum.now(tz="Europe/Paris"))


    @task(outlets=[raw_updated])
    def mark_raw_updated() -> None: 
        pass


    locations = get_pending_task()

    load.expand(task_to_load=locations) >> mark_raw_updated() #type: ignore

load_to_db()



