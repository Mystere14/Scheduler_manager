import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import session, select

from database import engine
from models import session, sessionRead, sessionCreate, sessionUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/session",
    tags=["session"],
)


@router.get("/", response_model=List[sessionRead])
def get_session():
    """
    Get all sessions.
    """
    with session(engine) as session:
        sessions = session.exec(select(session)).all()
        return sessions


@router.post("/", response_model=sessionRead)
def create_session(session_data: sessionCreate):
    """
    Create a new session.
    """
    new_session = session.model_validate(session_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_session)
            return new_session
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating session %s", session_data.code)
            raise HTTPException(
                status_code=409, detail=f"Session with code '{session_data.code}' already exists"
            ) from exc


@router.put("/{code}", response_model=sessionRead)
def update_session(code: str, session_data: sessionUpdate):
    """
    Update a teacher code by code.
    """
    with Session(engine) as session:
        session_record = session.get(session, code)
        if not session_record:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update only provided fields
        update_data = session_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(update_data, key, value)
        
        try:
            save_to_db(session, update_data)
            return update_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating session %s", code)
            raise HTTPException(
                status_code=409, detail=f"Error updating session with code '{code}'"
            ) from exc


@router.delete("/")
def delete_session():
    """
    Delete every session.
    """
    with Session(engine) as session:
        session.exec(delete(session))
        session.commit()
        
        return {"message": "All session entries deleted successfully"}
