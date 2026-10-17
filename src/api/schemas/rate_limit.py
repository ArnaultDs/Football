from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RateLimitResponse(BaseModel): 
    model_config = ConfigDict(from_attributes=True)
    id: int 
    api_name: str
    window_start: datetime
    window_reset_at: datetime
    limit_total: int
    reserved_count: int 
    confirmed_count: int
    last_confirmed_at: datetime | None = None
    updated_at: datetime
