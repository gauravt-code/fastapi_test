from sqlmodel import Session, create_engine, SQLModel
from typing import Annotated
from fastapi import Depends

DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL)

def create_db_table():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session