from .receiver_model import *
from .item_model import *
from sqlmodel import SQLModel, create_engine, Session


engine = create_engine("sqlite:///database.db")
session = Session(engine)


def create_db_and_tables():
    """Create the database and tables."""
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully.")