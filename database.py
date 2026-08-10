from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This creates/connects to rooms.db file in the same folder
DATABASE_URL = "sqlite:///./rooms.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite only
)

# Each request gets its own DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our table models
Base = declarative_base()


# Dependency — gives a DB session to each route, closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
