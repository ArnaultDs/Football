from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.dialects.postgresql import insert

import logging

from common.infra.postgres import get_session_factory
from db.control.models import TaskRunInstance


logger = logging.getLogger(__name__)

MAX_ERROR_LENGTH = 2000

class TaskRunRecord(BaseModel): 
    model_config = ConfigDict(frozen=True)

    dag_id: str
    run_id: str
    task_id: str
    map_index: int
    try_number: int
    status: str
    started_at: datetime | None 
    ended_at: datetime | None
    error_type: str | None = None
    error_message: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


def write_task_run(record: TaskRunRecord, session: sessionmaker[Session] | None = None) -> None: 

    session_factory = session or get_session_factory()

    stmt = (
        insert(TaskRunInstance)
        .values(
            record.model_dump()
        )
        .on_conflict_do_update(
            index_elements=["dag_id", "run_id", "task_id", "map_index", "try_number"],
            set_={
                "status":record.status, 
                "ended_at": record.ended_at, 
                "error_type": record.error_type, 
                "error_message": record.error_message, 
                "metrics": record.metrics}
        )
    )

    with session_factory.begin() as s: 
        s.execute(stmt)

    logger.info(
        "task run recorded dag_id=%s task_id=%s map_index=%s try=%s status=%s", 
        record.dag_id, record.task_id, record.map_index, record.try_number, record.status)

