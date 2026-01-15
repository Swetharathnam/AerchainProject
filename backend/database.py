from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from config import settings

# Database Configuration
DATABASE_URL = settings.DATABASE_URL

# Need connect_args = {"check_same_thread": False} only for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
