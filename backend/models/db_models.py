"""SQLAlchemy ORM models for the SQLite job queue."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    url = Column(Text, nullable=False)
    title = Column(String, nullable=True)
    status = Column(String, default="pending")
    playlist_id = Column(String, nullable=True)
    playlist_index = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))


class ErrorLog(Base):
    __tablename__ = "error_log"
    id = Column(String, primary_key=True)
    job_id = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    retryable = Column(Integer, default=1)


_db_path = settings.resolve_path(settings.sqlite_db_path)
_db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{_db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(engine)
