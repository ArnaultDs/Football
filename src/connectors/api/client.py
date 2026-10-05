from typing import Any, Protocol
from pydantic import BaseModel
import requests
from logging import getLogger

logger = getLogger(__name__)

class ApiError(Exception): 
    pass

class ApiResponse(BaseModel): 
    data: dict[str, Any]
    headers: dict[str, str]

    def has_data_in_response(self) -> bool: 

        if not self.data["response"]: 
            return False

        return True
        


class PageFetcher(Protocol): 
    def fetch_page(
        self, 
        endpoint: str, 
        params: dict[str, Any]
    ) -> ApiResponse: 
        ...

class ApiClient: 
    def __init__(
        self, 
        base_url: str,
        headers: dict[str, str], 
        timeout: float = 30
    ) -> None: 

        self._base_url = base_url
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(headers)

    def fetch_page(self, endpoint: str, params:dict[str, Any]) -> ApiResponse: 
        logger.info("Fetching %s with %s", endpoint, params)
        response = self._session.get(
            f"{self._base_url}/{endpoint}", params=params, timeout=self._timeout
        )
        response.raise_for_status()

        data = response.json()
        if data.get("errors"):
            raise ApiError(f"{endpoint}: {data['errors']}")

        return ApiResponse(data=data, headers={k.lower(): v for k, v in response.headers.items()})