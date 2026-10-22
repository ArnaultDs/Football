from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, update, func, case, Executable
from sqlalchemy.dialects.postgresql import insert
import pendulum
from typing import Any
from abc import ABC

from db.control.models import ApiExtractionManifestInstance, DbtManifestInstance, ManifestStatus
from common.infra.postgres import get_session_factory


def _run_in_transaction(session_factory: sessionmaker[Session], *statements: Executable) -> None: 
    with session_factory.begin() as session: 
        for statement in statements: 
            session.execute(statement)


class ExtractionManifestRepository: 

    MAX_ATTEMPS = 3

    def __init__(self, session: sessionmaker[Session] | None = None) -> None: 

        self._session = session or get_session_factory()


    def register(
        self,
        *,
        api_name: str,
        endpoint:str, 
        page: int, 
        extracted_at: pendulum.DateTime, 
        location:str, 
        params:dict[str, Any], 
        dag_name: str
    ) -> None: 

        # define insert statement
        stmt = (
            insert(ApiExtractionManifestInstance)
            .values(
                api_name = api_name, 
                endpoint = endpoint, 
                page_number = page, 
                api_extracted_at = extracted_at, 
                location = location, 
                params=params,
                dag_name = dag_name
            )
            .on_conflict_do_update(
                index_elements=["location"], 
                set_={
                    "ingested_status": ManifestStatus.PENDING,
                    "api_extracted_at": extracted_at, 
                    "params": params, 
                    "dag_name": dag_name
                }
            )
        )

        # execute insert statement
        _run_in_transaction(self._session, stmt)


    def mark_succeeded(self, location: str) -> None: 

        # define update statement 
        stmt = (
            update(ApiExtractionManifestInstance)
            .where(
                ApiExtractionManifestInstance.location == location, 
            )
            .values(
                ingested_status = "succeeded",
                ingested_at = pendulum.now(tz="Europe/Paris"),
                attemps = 0, 
                last_error = None
            )
        )

        # execute update statement
        _run_in_transaction(self._session, stmt)

    def mark_failed(self, location: str, error: str) -> None:

        # define update statement 
        stmt = (
            update(ApiExtractionManifestInstance)
            .where(
                ApiExtractionManifestInstance.location == location, 
            )
            .values(
                attemps = ApiExtractionManifestInstance.attempts + 1,
                last_error = error[:2000],
                ingested_status = case(
                    (ApiExtractionManifestInstance.attempts + 1 >= self.MAX_ATTEMPS, "failed"),
                    else_="pending"
                ),
            )
        )

        # execute update statement
        _run_in_transaction(self._session, stmt)


    def list_pending(self) -> list[dict[str, Any]]: 

        m = ApiExtractionManifestInstance
        # define select statement 
        stmt = (
            select(m.id, m.location, m.endpoint, m.api_extracted_at)
            .where(
                m.ingested_status == "pending"
            )
            .order_by(m.api_extracted_at.asc())
        )

        # execute select statement and return 
        with self._session.begin() as session: 
            return [
                {
                    "id": id, 
                    "location": loc, 
                    "endpoint": ep, 
                    "api_extracted_at": eat
                } for id, loc, ep, eat in session.execute(stmt)
            ]


class DbtRunQueue: 

    MAX_ATTEMPS = 3

    def __init__(self, session: sessionmaker[Session] | None = None) -> None: 

        self._session = session or get_session_factory()

    def enqueue(self, raw_table: str, ingested_at: pendulum.DateTime) -> None:

        # define update statement
        update_stmt = (
            update(DbtManifestInstance)
            .where(
                DbtManifestInstance.raw_table_name == raw_table,
                DbtManifestInstance.dbt_ingested_status == "pending",
            )
            .values(dbt_ingested_status="superseded")
        )

        insert_stmt = (
            insert(DbtManifestInstance).values(
                raw_table_name=raw_table,
                staging_table_name = f"stg_{raw_table}",
                raw_ingested_at=ingested_at,
            )
        )

        _run_in_transaction(self._session, update_stmt, insert_stmt)

    def mark_succeeded(self, manifest_id: int) -> None: 

        # define update statement
        stmt = (
            update(DbtManifestInstance)
            .where(
                DbtManifestInstance.id == manifest_id
            )
            .values(
                dbt_ingested_status = "succeeded",
                dbt_ingested_at = pendulum.now(tz="Europe/Paris"),
                attemps = 0, 
                last_error = None
            )
        )

        # execute update statement
        _run_in_transaction(self._session, stmt)

    def mark_failed(self, manifest_id: int, error: str) -> None: 

        # define update statement 
        stmt = (
            update(DbtManifestInstance)
            .where(
                DbtManifestInstance.id == manifest_id
            )
            .values(
                attemps = DbtManifestInstance.attempts + 1,
                last_error = error[:2000],
                dbt_ingested_status = case(
                    (DbtManifestInstance.attempts + 1 >= self.MAX_ATTEMPS, "failed"),
                    else_="pending"
                ),
            )
        )

        _run_in_transaction(self._session, stmt)

    def list_pending(self) -> list[dict[str, Any]]:

        m = DbtManifestInstance

        # define select statement 
        stmt = (
            select(m.id, m.raw_table_name, m.staging_table_name)
            .where(
                m.dbt_ingested_status == "pending"
            )
        )

         # execute select statement and return 
        with self._session.begin() as session: 
            return [
                {
                    "id": id, 
                    "raw": raw, 
                    "staging": stg
                } for id, raw, stg in session.execute(stmt)
            ]