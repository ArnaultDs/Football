from typing import Any
from airflow.sdk import dag, task



from common.api_extraction_task import extract_from_api_load_to_minio


@dag(schedule="0 4 * * 3#1", catchup=False)
def setup(season: int = 2026, league: int = 61): 

    @task
    def build_setup_requests(league: int, season: int) -> list[dict[str, Any]]: 
        return [
            {"endpoint": "leagues", "league": league, "season": season}, 
            {"endpoint": "teams", "league": league, "season": season}, 
            {"endpoint": "fixtures", "league": league, "season": season}
        ]

    endpoint_requests = build_setup_requests(league=league, season=season)

    extract_from_api_load_to_minio\
        .partial(api_name="football_api")\
        .expand(request_param=endpoint_requests)

setup()