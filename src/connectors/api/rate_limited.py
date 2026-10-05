from typing import Any
import pendulum

from connectors.api.client import PageFetcher, ApiResponse
from db.control.rate_limiter import RateLimiter, QuotaExhausted

def seconds_until_next_utc_midnight() -> int:
    now = pendulum.now("UTC")
    next_midnight = now.add(days=1).start_of("day")
    return int((next_midnight - now).total_seconds())

class RateLimitedClient: 
    def __init__(self, client: PageFetcher, limiter: RateLimiter) -> None: 
        self._client = client 
        self._limiter = limiter

    def fetch_page(self, endpoint: str, params: dict[str, Any]) -> ApiResponse: 

        if not self._limiter.try_reserve(): 
            raise QuotaExhausted(f"Request to api has exceeded its quota of {self._limiter.API_RATE_LIMIT} calls")

        response = self._client.fetch_page(endpoint, params)

        reset = response.headers.get("x-ratelimit-requests-reset", None)
        reset_seconds = int(reset) if reset is not None else seconds_until_next_utc_midnight()
        self._limiter.confirm(
            remaining = int(response.headers["x-ratelimit-requests-remaining"]), 
            reset_seconds = reset_seconds
        )

        return response
