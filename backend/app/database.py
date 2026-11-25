import os
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Local default: a SQLite file (survives restarts). In production set DATABASE_URL
# to a hosted Postgres URL so data survives redeploys too.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./patients.db")

# Hosted providers often give "postgres://" or "postgresql://"; SQLAlchemy wants a driver name.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    ward = Column(String(50), nullable=False, index=True)
    department = Column(String(50), nullable=False, index=True)
    doctor = Column(String(80), nullable=False, index=True)
    admission_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="Admitted")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
