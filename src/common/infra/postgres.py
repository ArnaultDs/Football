from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine, Engine
from functools import cache

from common.config import get_settings

class Base(DeclarativeBase): 
    pass

@cache
def get_engine() -> Engine:
    return create_engine(get_settings().postgres_database_url, pool_pre_ping=True)

@cache 
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
