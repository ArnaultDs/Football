import pendulum
from typing import Any
from logging import getLogger
from airflow.sdk import task, get_current_context
from connectors.api.interface import api_interface
from connectors.api.api import get_api_client
from connectors.storage.minio_storage import MinioConnector
from db.control.manifest import ApiExtractionManifest


logger = getLogger(__name__)

@task
def extract_from_api_load_to_minio(
    api_name: str, 
    request_param: dict[str, Any], 
) -> str | None: 

    logger.info("Starting extraction from api '%s' and load to minio ...", request_param["endpoint"])

    # Airflow context
    ti = get_current_context().get("ti")
    if ti is None: 
        raise RuntimeError("No task in the context : called outside a task ?")

    # get partition date from requests
    request = dict(request_param)
    partition_date = request.pop("run_date", None)


    # extract from api
    interface = api_interface.validate_python(request)
    api_client = get_api_client(api_name)
    response = api_client.fetch_page(interface.endpoint, interface.params)

    # Verify response
    if not response.has_data_in_response(): 
        logger.info("No data to extract for %s", request)
        return None

    # load to minio
    minio_client = MinioConnector(bucket="bronze")
    minio_path = minio_client.load(response.data, api_name, interface.file_name, interface.partitions, partition_date)

    logger.info("Successfully extracted from api and loaded to minio")

    # create manifest control
    manifest_client = ApiExtractionManifest()
    manifest_client.create(
        api_name=api_name,
        endpoint=interface.endpoint,
        paging=interface.page,
        extracted_at=pendulum.now(tz="Europe/Paris"),
        location=minio_path, 
        params=interface.params,
        dag_name=ti.dag_id
    )

    logger.info("Manifest created for %s", minio_path)
    
    return minio_path


    

    
    

    
    




    