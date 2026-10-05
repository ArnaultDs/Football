from typing import Any
from sqlalchemy import Engine, text, bindparam
from sqlalchemy.dialects.postgresql import JSONB
from logging import getLogger
import pendulum

from common.postgres import engine

logger = getLogger(__name__)
class DatabaseConnector: 

    def __init__(self, current_engine: Engine | None = None) -> None: 

        self._engine = current_engine or engine

    def create_table(self, table_name: str) -> None: 

        create_stmt = f"""
            CREATE TABLE IF NOT EXISTS raw.{table_name} (
                source_file text NOT NULL, 
                payload jsonb NOT NULL,
                loaded_at timestamptz NOT NULL DEFAULT now(), 
                api_extracted_at timestamptz NOT NULL
            )
        """

        with self._engine.begin() as connection:
            connection.execute(text(create_stmt))

    def load(self, table_name: str, source_file: str, payload:dict[str, Any], api_extracted_at: pendulum.DateTime) -> None: 

        logger.info("Fetching payload to raw.'%s'", table_name)
        
        delete_stmt = text(f"DELETE FROM raw.{table_name} WHERE source_file = :source_file")

        insert_stmt = text(
            f"INSERT INTO raw.{table_name} (source_file, payload, api_extracted_at) VALUES (:source_file, :payload, :at)"
        ).bindparams(bindparam("payload", type_=JSONB))

        self.create_table(table_name)
        with self._engine.begin() as connection:
            connection.execute(delete_stmt, {"source_file": source_file})
            connection.execute(insert_stmt, {"source_file": source_file, "payload": payload, "at": api_extracted_at})

    def read(self, query: str) -> list[dict[str, Any]]: 

        with self._engine.begin() as connection: 
            result = connection.execute(text(query))
            return [dict(row) for row in result.mappings()]



