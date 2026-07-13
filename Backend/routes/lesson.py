import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import Session, select

from database import engine
from models import lesson, lessonRead, lessonCreate, lessonUpdate
from utils import saveToDb

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/lesson",
    tags=["lesson"],
)


@router.get("/", response_model=List[lessonRead])
def getLesson():
    """
    Get all lessons.
    """
    with Session(engine) as session:
        sessions = session.exec(select(lesson)).all()
        return sessions

@router.get("/getTrueLesson", response_model=List[lessonRead])
def getTrueLesson():
    """
    Get all true lessons.
    """
    with Session(engine) as session:
        sessions = session.exec(select(lesson).where(lesson.isLesson == True)).all()
        return sessions

@router.get("/getFalseLesson", response_model=List[lessonRead])
def getFalseLesson():
    """
    Get all false lessons.
    """
    with Session(engine) as session:
        sessions = session.exec(select(lesson).where(lesson.isLesson == False)).all()
        return sessions

@router.post("/", response_model=lessonRead)
def createLesson(lessonData: lessonCreate):
    """
    Create a new lesson.
    """
    newLesson = lesson.model_validate(lessonData)

    with Session(engine) as session:
        try:
            saveToDb(session, newLesson)
            return newLesson
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating lesson %s", lessonData.code)
            raise HTTPException(
                status_code=409, detail=f"Lesson with code '{lessonData.code}' already exists"
            ) from exc


@router.put("/{code}", response_model=lessonRead)
def updateLesson(code: str, lessonData: lessonUpdate):
    """
    Update a lesson by code.
    """
    with Session(engine) as session:
        lessonRecord = session.get(lesson, code)
        if not lessonRecord:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Update only provided fields
        updateData = lessonData.model_dump(exclude_unset=True)
        for key, value in updateData.items():
            setattr(lessonRecord, key, value)
        
        try:
            saveToDb(session, lessonRecord)
            return updateData
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating lesson %s", code)
            raise HTTPException(
                status_code=409, detail=f"Error updating lesson with code '{code}'"
            ) from exc


@router.delete("/")
def deleteLesson():
    """
    Delete every lesson.
    """
    with Session(engine) as session:
        session.exec(delete(lesson))
        session.commit()
        
        return {"message": "All lesson entries deleted successfully"}


@router.delete("/trueLesson")
def deleteTrueLesson():
    """
    Delete every true lesson.
    """
    with Session(engine) as session:
        session.exec(delete(lesson).where(lesson.isLesson == True))
        session.commit()
        
        return {"message": "All lesson entries deleted successfully"}
