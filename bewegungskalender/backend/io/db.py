from sqlalchemy import Engine
from sqlmodel import create_engine, SQLModel, Session

from bewegungskalender.backend.io.cli import DB_MODE
from bewegungskalender.backend.io.config import DATADIR, SYNC_DB_FILE, SEARCH_DB_FILE

_SYNC_SQLITE_URL: str = f"sqlite:///{DATADIR}/{SYNC_DB_FILE}"
_SYNC_ENGINE: Engine = create_engine(_SYNC_SQLITE_URL)
_SEARCH_SQLITE_URL: str = f"sqlite:///{DATADIR}/{SEARCH_DB_FILE}"
_SEARCH_ENGINE: Engine = create_engine(_SEARCH_SQLITE_URL)

def session() -> Session:
    engine = _SEARCH_ENGINE if DB_MODE == 'search' else _SYNC_ENGINE
    with Session(engine) as sess:
        return sess

def create_tables() -> None:
    SQLModel.metadata.create_all(_SYNC_ENGINE)

def recreate_tables() -> None:
    """
    recreates the database tables for the SQLModel Classes that have the 'table=True' flag and have already been imported.
    """
    SQLModel.metadata.drop_all(_SEARCH_ENGINE) # Quick fix
    SQLModel.metadata.create_all(_SEARCH_ENGINE)

def exe(statement):
    return session().exec(statement)