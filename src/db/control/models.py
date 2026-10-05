from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, DateTime, BIGINT, UniqueConstraint, Identity, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Any

from common.postgres import Base


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
    last_error: Mapped[str|None] = mapped_column(default=None, nullable=True)

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
    last_error: Mapped[str|None] = mapped_column(default=None, nullable=True)