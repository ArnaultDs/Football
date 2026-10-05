from typing import Any
from pendulum import Date

from connectors.database.database_storage import DatabaseConnector

def get_fixtures_to_do(limit: int = 10) -> list[dict[str, Any]]: 
    stmt = f"select id, league_id, league_season, api_name from ops.fixtures_statistics_todo limit {limit}"

    connector = DatabaseConnector()
    return connector.read(stmt)

def get_players_profile_todo(limit: int = 10) -> list[dict[str, Any]]: 

    stmt = f"select team_id from ops.players_profile_todo limit {limit}"
    
    connector = DatabaseConnector()
    return connector.read(stmt)    

def get_fixtures_played_by_date(run_date: Date | None = None) -> list[dict[str, Any]]: 

    stmt = f"select distinct(id) as fixture_id from marts.fixtures where 1=1"

    if run_date: 
        stmt = f"{stmt} and game_date = '{run_date}'"

    connector = DatabaseConnector()
    return connector.read(stmt)
