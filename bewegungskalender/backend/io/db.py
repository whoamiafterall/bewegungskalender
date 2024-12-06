from sqlalchemy import Engine
from sqlmodel import create_engine, SQLModel, Session

from bewegungskalender.backend.io.config import DB_FILE, DATADIR

_SQLITE_URL: str = f"sqlite:///{DATADIR}/{DB_FILE}"
_ENGINE: Engine = create_engine(_SQLITE_URL)

def session() -> Session:
    with Session(_ENGINE) as sess:
        return sess

def create_tables() -> None:
    """
    Creates the database tables for the SQLModel Classes that have the 'table=True' flag and have already been imported.
    """
    SQLModel.metadata.drop_all(_ENGINE) # Quick fix
    SQLModel.metadata.create_all(_ENGINE)

def exe(statement):
    return session().exec(statement)