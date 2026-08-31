from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger
from app.models import Base

import os
import tempfile

# SQLAlchemy engine initialization with database connection pool and automatic local fallback
def init_engine():
    db_url = settings.DATABASE_URL
    is_localhost = "localhost" in db_url or "127.0.0.1" in db_url
    
    # If unconfigured/localhost in production serverless, fallback immediately to SQLite without waiting for TCP timeout
    if is_localhost and settings.APP_ENV == "production":
        db_path = os.path.join(tempfile.gettempdir(), "verticare.db")
        return create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )

    try:
        connect_args = {"connect_timeout": 2} if db_url.startswith("postgresql") else {}
        eng = create_engine(
            db_url,
            echo=bool(settings.DEBUG),
            pool_pre_ping=True,
            connect_args=connect_args
        )
        # Actively test connection to verify database reachability
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected to primary database at {settings.DATABASE_URL}")
        return eng
    except Exception as e:
        logger.warning(f"Primary database connection failed ({e}). Initializing local SQLite database fallback.")
        db_path = os.path.join(tempfile.gettempdir(), "verticare.db")
        return create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )


engine = init_engine()

# Automatically create all required tables
Base.metadata.create_all(bind=engine)


def sync_schema_columns(eng):
    """Safely ensures missing nullable columns in Base.metadata exist without data loss."""
    try:
        with eng.connect() as conn:
            if eng.dialect.name == "sqlite":
                for table_name, table in Base.metadata.tables.items():
                    res = conn.execute(text(f"PRAGMA table_info({table_name});")).fetchall()
                    existing_cols = {row[1] for row in res}
                    for col in table.columns:
                        if col.name not in existing_cols:
                            col_type = "JSON" if "JSON" in str(col.type).upper() else str(col.type)
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type};"))
                            conn.commit()
                            logger.info(f"Added missing column '{col.name}' to table '{table_name}'")
    except Exception as e:
        logger.warning(f"Schema sync notice: {e}")


sync_schema_columns(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency for yielding database sessions."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
