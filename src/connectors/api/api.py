from common.settings import settings
from connectors.api.client import PageFetcher, ApiClient
from connectors.api.rate_limited import RateLimitedClient
from db.control.rate_limiter import RateLimiter

def rapid_api_client() -> PageFetcher: 
    client = ApiClient(
        base_url=settings.rapid_api_base_url, 
        headers = {"x-rapidapi-key": settings.x_rapidapi_key, "x-rapidapi-host": settings.x_rapidapi_host}
    )

    return RateLimitedClient(client, RateLimiter("rapid_api"))


def football_api_client() -> PageFetcher: 
    client = ApiClient(
        base_url=settings.football_api_base_url, 
        headers = {'x-apisports-key': settings.x_apisports_key}
    )

    return RateLimitedClient(client, RateLimiter("football_api"))


def get_api_client(name: str) -> PageFetcher: 
    if name == "rapid_api": 
        return rapid_api_client()

    return football_api_client()
