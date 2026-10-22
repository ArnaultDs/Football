from typing import Any
from pendulum import Date

from connectors.database.raw import DatabaseConnector


def get_fixtures_played_by_date(run_date: Date | None = None) -> list[dict[str, Any]]: 

    stmt = f"select distinct(fixture_id) as fixture_id from marts.fact_matches where 1=1"

    params: dict[str, Any] = {}
    if run_date is not None: 
        stmt += " where kickoff_at::date = :run_date"
        params["run_date"] = run_date

    connector = DatabaseConnector()
    return connector.read(stmt, params)
