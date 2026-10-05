from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
from common.assets import raw_updated   
from typing import Any

from db.control.manifest import DbtManifest

DBT = "cd /opt/dbt/football_dbt && /home/airflow/dbt-venv/bin/dbt"

@dag(schedule=[raw_updated], max_active_runs=1, catchup=False)
def dbt_build():

    @task
    def claim() -> list[dict[str, Any]]: 
        return DbtManifest().claim_pending()

    @task.short_circuit
    def has_pending(claimed: list[dict[str, Any]]) -> bool: 
        return bool(claimed)

    @task.bash
    def build(claimed: list[dict[str, Any]]) -> str: 
        tables = sorted({c["raw"] for c in claimed})
        selectors = " ".join(f"source:raw.{t}+" for t in tables)
        return f"{DBT} build --target prod -s {selectors}"

    @task(trigger_rule="all_success")
    def mark_success(claimed: list[dict[str, Any]]): 
        for claim in claimed: 
            DbtManifest().succeeded(claim["id"])

    @task(trigger_rule="one_failed")
    def mark_fail(claimed: list[dict[str, Any]]): 
        for claim in claimed: 
            DbtManifest().failed(claim["id"], "dbt error")

    claimed = claim()
    built = build(claimed) #type: ignore

    has_pending(claimed) >> built >> [mark_success(claimed), mark_fail(claimed)] #type: ignore

dbt_build()