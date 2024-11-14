from sqlmodel import create_engine, SQLModel

from bewegungskalender.backend.io.config import DB_FILE, DATADIR

_SQLITE_URL = f"sqlite:///{DATADIR}/{DB_FILE}"

ENGINE = create_engine(_SQLITE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(ENGINE)