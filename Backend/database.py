"""
Database configuration and session management.
"""
import logging


from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from config import settings

import models 

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    """
    Initialize the database by creating all tables.
    """

    #SQLModel.metadata.drop_all(engine) # activate this line to update the database schema (drop all tables and recreate them)

    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database tables created successfully")


def get_session():
    """
    Provide a transactional scope around a series of operations.
    """
    with Session(engine) as session:
        yield session

