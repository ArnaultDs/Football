from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from common.config import settings

class Base(DeclarativeBase): 
    pass

engine = create_engine(settings.postgres_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
