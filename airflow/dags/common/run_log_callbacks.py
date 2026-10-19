from airflow.sdk import Context
from datetime import datetime, UTC
import logging

from observability.run_log import TaskRunRecord, write_task_run, MAX_ERROR_LENGTH
from db.control.models import TaskRunStatus

logger = logging.getLogger(__name__)

def _to_record(context: Context, status: str) -> TaskRunRecord: 
    
    ti = context["ti"] #type: ignore
    dag_id = ti.dag_id
    run_id = ti.run_id
    task_id = ti.task_id
    map_index = ti.map_index if ti.map_index is not None else -1
    try_number = ti.try_number
    start_date = ti.start_date
    end_date = ti.end_date or datetime.now(UTC)
    error = context.get("exception")
    error_type = type(error).__name__ if isinstance(error, BaseException) else None
    error_message = str(error)[:MAX_ERROR_LENGTH] if error is not None else None

    return TaskRunRecord(
        dag_id=dag_id, run_id=run_id, task_id=task_id, map_index=map_index, 
        try_number=try_number, status=status, started_at=start_date, 
        ended_at=end_date, error_type=error_type, error_message=error_message, metrics={}
    )


def record_success(context: Context) -> None: 

    ti = context["ti"] #type: ignore
    try: 
        write_task_run(_to_record(context, TaskRunStatus.SUCCESS))
    except: 
        logger.exception("run log write failed dag_id=%s task_id=%s", ti.dag_id, ti.task_id)

def record_failure(context: Context) -> None:
    ti = context["ti"] #type: ignore
    try: 
        write_task_run(_to_record(context, TaskRunStatus.FAILED))
    except: 
        logger.exception("run log write failed dag_id=%s task_id=%s", ti.dag_id, ti.task_id)

def record_retry(context: Context) -> None:
    ti = context["ti"] #type: ignore
    try: 
        write_task_run(_to_record(context, TaskRunStatus.UP_FOR_RETRY))
    except: 
        logger.exception("run log write failed dag_id=%s task_id=%s", ti.dag_id, ti.task_id)

RUN_LOG_CALLBACKS = {
    "on_success_callback": record_success,
    "on_failure_callback": record_failure, 
    "on_retry_callback": record_retry
}