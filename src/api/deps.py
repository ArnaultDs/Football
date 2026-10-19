import hashlib
from typing import Annotated
from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException, status
from datetime import UTC, datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from common.postgres import SessionLocal
from db.control.models import ApiKeyInstance

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_db(): 
    db = SessionLocal()

    try: 
        yield db 
    finally: 
        db.close()


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def get_api_key(
    key: Annotated[str | None, Depends(api_key_header)],
    db: Annotated[Session, Depends(get_db)],
):
    if key is None: 
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing API key")

    api_key = db.scalar(
        select(ApiKeyInstance)
        .where(
            ApiKeyInstance.key_hash == hash_key(key), 
            ApiKeyInstance.is_active)
    )

    if api_key is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")

    api_key.last_used_at = datetime.now(UTC)

    return api_key