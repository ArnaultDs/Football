from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ExtractionManifestResponse(BaseModel): 
    model_config = ConfigDict(from_attributes=True)
    id: int 
    api_name: str
    endpoint: str
    page_number: int
    location: str
    ingested_status: str 
    ingested_at: datetime | None = None
    api_extracted_at: datetime
    dag_name: str
    attempts: int
    last_error: str | None = None
