from airflow.sdk import dag, task , get_current_context
from typing import Any
import pendulum

from logging import getLogger


from connectors.database.queries import get_fixtures_played_by_date
from common.api_extraction_task import extract_from_api_load_to_minio


logger = getLogger(__name__)


@dag(schedule="0 2 * * 5-1", catchup=False)
def weekend_batch(season: int = 2026, league: int = 61) -> None: 

    @task
    def get_target_date(logical_date: pendulum.DateTime | None = None) -> pendulum.DateTime: 
        return (logical_date or pendulum.now("UTC")).in_tz("Europe/Paris").subtract(days=1)

    @task 
    def get_fixtures_available_games(run_date: pendulum.DateTime) -> list[dict[str, Any]]: 
        return get_fixtures_played_by_date(run_date.date())

    @task.short_circuit
    def check_available_games(fixtures_played: list[dict[str, Any]]) -> bool: 
        
        if not fixtures_played: 
            return False

        return True

    @task 
    def get_fixtures_params(
        run_date: pendulum.DateTime,
        league: int, 
        season: int, 
        id: int | None = None, 
    ) -> dict[str, Any]: 
        
        return {
            "endpoint": "fixtures", 
            "id": id, 
            "league": league, 
            "season": season, 
            "date": run_date.date().strftime("%Y-%m-%d"), 
            "run_date": run_date
        }

    @task
    def get_fixtures_players_params(
        run_date: pendulum.DateTime,
        fixture: dict[str, Any], 
        league: int, 
        season: int, 
    ) -> dict[str, Any]: 
        
        return {
            "endpoint": "fixtures/players", 
            "fixture": fixture["fixture_id"], 
            "league": league, 
            "season": season, 
            "run_date": run_date
        }

    target_date = get_target_date()

    fixtures_played = get_fixtures_available_games(target_date) #type: ignore

    constraints = check_available_games(fixtures_played) #type: ignore

    fixture_params = get_fixtures_params(target_date, league, season) #type: ignore

    extract_fixtures = extract_from_api_load_to_minio(api_name="football_api", request_param=fixture_params) #type: ignore

    fixtures_players_params = get_fixtures_players_params.partial(
        run_date = target_date, 
        league = league, 
        season = season
    ).expand(fixture=fixtures_played)

    extract_stat = extract_from_api_load_to_minio\
        .partial(api_name="football_api")\
        .expand(request_param=fixtures_players_params)

    target_date >> fixtures_played >> constraints >> fixture_params >> extract_fixtures >> fixtures_players_params >> extract_stat #type: ignore

weekend_batch()