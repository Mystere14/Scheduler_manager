"""
Utility functions for the application.
"""
from sqlmodel import Session


def save_to_db(session: Session, obj):
    """
    Save an object to the database.
    
    Args:
        session: SQLModel session
        obj: Object to save
    """
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
