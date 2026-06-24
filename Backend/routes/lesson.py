import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import Session, select

from database import engine
from models import lesson, lessonRead, lessonCreate, lessonUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/lesson",
    tags=["lesson"],
)


@router.get("/", response_model=List[lessonRead])
def get_lesson():
    """
    Get all lessons.
    """
    with Session(engine) as session:
        sessions = session.exec(select(lesson)).all()
        return sessions


@router.post("/", response_model=lessonRead)
def create_lesson(lesson_data: lessonCreate):
    """
    Create a new lesson.
    """
    new_lesson = lesson.model_validate(lesson_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_lesson)
            return new_lesson
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating lesson %s", lesson_data.code)
            raise HTTPException(
                status_code=409, detail=f"Lesson with code '{lesson_data.code}' already exists"
            ) from exc


@router.put("/{code}", response_model=lessonRead)
def update_lesson(code: str, lesson_data: lessonUpdate):
    """
    Update a teacher code by code.
    """
    with Session(engine) as session:
        lesson_record = session.get(lesson, code)
        if not lesson_record:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Update only provided fields
        update_data = lesson_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(lesson_record, key, value)
        
        try:
            save_to_db(session, lesson_record)
            return update_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating lesson %s", code)
            raise HTTPException(
                status_code=409, detail=f"Error updating lesson with code '{code}'"
            ) from exc


@router.delete("/")
def delete_lesson():
    """
    Delete every lesson.
    """
    with Session(engine) as session:
        session.exec(delete(lesson))
        session.commit()
        
        return {"message": "All lesson entries deleted successfully"}
