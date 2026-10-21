from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, DateTime, BIGINT, CheckConstraint, UniqueConstraint, Identity, text, String
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Any
from enum import Enum

from common.infra.postgres import Base


class RapidApiLimiterInstance(Base): 
    __tablename__ = "api_rate_limiter"
    __table_args__ = (
        UniqueConstraint("api_name", "window_start", name="uq_rate_limiter"), 
        {"schema": "ctl"}
    )

    id: Mapped[int] = mapped_column(BIGINT, Identity(), primary_key=True)
    api_name: Mapped[str]
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))    
    limit_total: Mapped[int]
    reserved_count: Mapped[int] = mapped_column(default=0, server_default="0")
    confirmed_count: Mapped[int] = mapped_column(default=0, server_default="0")
    last_confirmed_at: Mapped[datetime|None]
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class ApiExtractionManifestInstance(Base): 
    __tablename__ = "api_extraction_manifest"
    __table_args__ = (
        UniqueConstraint("location", name="uq_extraction_manifest"), 
        {"schema": "ctl"}
    )
    id: Mapped[int] = mapped_column(BIGINT, Identity(), primary_key=True)
    location: Mapped[str]
    api_name: Mapped[str]
    endpoint: Mapped[str]
    page_number: Mapped[int]
    api_extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True)) 
    ingested_status: Mapped[str] = mapped_column(default="pending")
    ingested_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True)) 
    params: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    dag_name: Mapped[str]
    attemps: Mapped[int] = mapped_column(default=0, server_default=text("0::int"))
    last_error: Mapped[str|None] = mapped_column(server_default=None, nullable=True)

class DbtManifestInstance(Base): 
    __tablename__ = "dbt_manifest"
    __table_args__ = (
            UniqueConstraint("raw_table_name", "raw_ingested_at", name="uq_dbt_manifest"), 
            {"schema": "ctl"}
        )

    id: Mapped[int] = mapped_column(BIGINT, Identity(), primary_key=True)
    raw_table_name: Mapped[str]
    staging_table_name: Mapped[str]
    raw_ingested_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True)) 
    dbt_ingested_status: Mapped[str] = mapped_column(default="pending")
    dbt_ingested_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True)) 
    attemps: Mapped[int] = mapped_column(default=0, server_default=text("0::int"))
    last_error: Mapped[str|None] = mapped_column(server_default=None, nullable=True)


class ApiKeyInstance(Base): 
    __tablename__ = "api_key"
    __table_args__ = {"schema": "ctl"}

    id: Mapped[int] = mapped_column(BIGINT, Identity(), primary_key=True)
    name: Mapped[str]
    scope: Mapped[str] = mapped_column(server_default=text("'read'"))
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_used_at: Mapped[datetime | None]


class TaskRunStatus(str, Enum): 
    SUCCESS = "success"
    FAILED = "failed"
    UP_FOR_RETRY = "up_for_retry"

_STATUS_VALUES = ", ".join(f"'{s.value}'" for s in TaskRunStatus)

class TaskRunInstance(Base): 
    __tablename__ = "task_run"
    __table_args__ = (
        UniqueConstraint("dag_id", "run_id", "task_id", "map_index", "try_number", name="uq_task_run"), 
        CheckConstraint(f"status in ({_STATUS_VALUES})", name="ck_task_run_status"),
        {"schema": "ctl"}

    )

    id: Mapped[int] = mapped_column(BIGINT, Identity(), primary_key=True)
    dag_id: Mapped[str]
    run_id: Mapped[str]
    task_id: Mapped[str]
    map_index: Mapped[int] = mapped_column(default=-1)
    try_number: Mapped[int]
    status: Mapped[str] = mapped_column()
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)) 
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)) 
    error_type: Mapped[str | None]
    error_message: Mapped[str | None]
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())

class ApiName(str, Enum):
    RAPID_API = "rapid_api"
    FOOTBALL_API = "football_api"

_API_NAMES = ", ".join(f"'{a.value}'" for a in ApiName)


class SeasonRefInstance(Base):
    __tablename__ = "season_ref"
    __table_args__ = (
        CheckConstraint(f"api_name in ({_API_NAMES})", name="ck_season_ref_api_name"),
        {"schema": "ctl"},
    )
    id: Mapped[int] = mapped_column(BIGINT, Identity(), primary_key=True)
    league_id: Mapped[int]
    season: Mapped[int]
    api_name: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    backfill_enabled: Mapped[bool] = mapped_column(server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
