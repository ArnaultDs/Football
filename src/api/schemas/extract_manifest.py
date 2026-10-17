from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ExtractManifestResponse(BaseModel): 
    model_config = ConfigDict(from_attributes=True)
    id: int 
    api_name: str
    endpoint: str
    page_number: int
    location: str
    ingested_status: str 
    ingested_at: datetime
    api_extracted_at: datetime
    dag_name: str
    attemps: int
    last_error: str | None = None
