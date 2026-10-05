from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, func, case
from sqlalchemy.dialects.postgresql import insert
import pendulum
from typing import Any
from abc import ABC

from db.control.models import ApiExtractionManifestInstance, DbtManifestInstance
from common.postgres import SessionLocal

class Manifest(ABC): 

    def __init__(self, session: sessionmaker | None = None) -> None: 
        self._Session = session or SessionLocal

    def _execute_statement(self, stmt) -> None: 

        with self._Session.begin() as session: 
            session.execute(stmt)

    def _execute_many_statement(self, stmts) -> None: 

        with self._Session.begin() as session: 
            for stmt in stmts:
                session.execute(stmt)


class ApiExtractionManifest(Manifest): 

    MAX_ATTEMPS = 3

    def __init__(self, session: sessionmaker | None = None) -> None: 

        super().__init__(session)


    def create(
        self,
        api_name: str,
        endpoint:str, 
        paging: int, 
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
                page_number = str(paging), 
                api_extracted_at = extracted_at, 
                location = location, 
                params=params,
                dag_name = dag_name
            )
            .on_conflict_do_update(
                index_elements=["location"], 
                set_={
                    "ingested_status": "pending",
                    "api_extracted_at": extracted_at, 
                    "params": params, 
                    "dag_name": dag_name
                }
            )
        )

        # execute insert statement
        self._execute_statement(stmt)


    def succeeded(self, location: str) -> None: 

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
        self._execute_statement(stmt)

    def failed(self, location: str, error: str) -> None:

        # define update statement 
        stmt = (
            update(ApiExtractionManifestInstance)
            .where(
                ApiExtractionManifestInstance.location == location, 
            )
            .values(
                attemps = ApiExtractionManifestInstance.attemps + 1,
                last_error = error[:2000],
                ingested_status = case(
                    (ApiExtractionManifestInstance.attemps + 1 >= self.MAX_ATTEMPS, "failed"),
                    else_="pending"
                ),
            )
        )

        # execute update statement
        self._execute_statement(stmt)


    def claim_pending(self) -> list[dict[str, Any]]: 

        m = ApiExtractionManifestInstance
        # define select statement 
        stmt = (
            select(m.id, m.location, m.endpoint, m.api_extracted_at)
            .where(
                m.ingested_status == "pending"
            )
            .order_by(m.api_extracted_at.desc())
        )

        # execute select statement and return 
        with self._Session() as session: 
            return [
                {
                    "id": id, 
                    "location": loc, 
                    "endpoint": ep, 
                    "api_extracted_at": eat
                } for id, loc, ep, eat in session.execute(stmt)
            ]


class DbtManifest(Manifest): 

    MAX_ATTEMPS = 3

    def __init__(self, session: sessionmaker | None = None) -> None: 

        super().__init__(session)

    def create(self, table_name: str, ingested_at: pendulum.DateTime) -> None:

        # define update statement
        update_stmt = (
            update(DbtManifestInstance)
            .where(
                DbtManifestInstance.raw_table_name == table_name,
                DbtManifestInstance.dbt_ingested_status == "pending",
            )
            .values(dbt_ingested_status="superseded")
        )

        insert_stmt = (
            insert(DbtManifestInstance).values(
                raw_table_name=table_name,
                staging_table_name = f"stg_{table_name}",
                raw_ingested_at=ingested_at,
            )
        )

        self._execute_many_statement([update_stmt, insert_stmt])

    def succeeded(self, manifest_id: int) -> None: 

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
        self._execute_statement(stmt)

    def failed(self, manifest_id: int, error: str) -> None: 

        # define update statement 
        stmt = (
            update(DbtManifestInstance)
            .where(
                DbtManifestInstance.id == manifest_id
            )
            .values(
                attemps = DbtManifestInstance.attemps + 1,
                last_error = error[:2000],
                dbt_ingested_status = case(
                    (DbtManifestInstance.attemps + 1 >= self.MAX_ATTEMPS, "failed"),
                    else_="pending"
                ),
            )
        )

        self._execute_statement(stmt)

    def claim_pending(self) -> list[dict[str, Any]]:

        m = DbtManifestInstance

        # define select statement 
        stmt = (
            select(m.id, m.raw_table_name, m.staging_table_name)
            .where(
                m.dbt_ingested_status == "pending"
            )
        )

         # execute select statement and return 
        with self._Session() as session: 
            return [
                {
                    "id": id, 
                    "raw": raw, 
                    "staging": stg
                } for id, raw, stg in session.execute(stmt)
            ]