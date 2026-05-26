import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import Session, select

from database import engine
from models import compare_scheduler, compare_schedulerRead, compare_schedulerCreate, compare_schedulerUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/compare_scheduler",
    tags=["compare_scheduler"],
)


@router.get("/", response_model=List[compare_schedulerRead])
def get_compare_scheduler():
    """
    Get all compare schedulers.
    """
    with Session(engine) as session:
        codes = session.exec(select(compare_scheduler)).all()
        return codes


@router.post("/", response_model=compare_schedulerRead)
def create_compare_scheduler(compare_scheduler_data: compare_schedulerCreate):
    """
    Create a new teacher code.
    """
    new_compare_scheduler = compare_scheduler.model_validate(compare_scheduler_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_compare_scheduler)
            return new_compare_scheduler
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating compare_scheduler %s", compare_scheduler_data.code)
            raise HTTPException(
                status_code=409, detail=f"Compare_scheduler with code '{compare_scheduler_data.code}' already exists"
            ) from exc


@router.put("/{code}", response_model=compare_schedulerRead)
def update_compare_scheduler(code: str, compare_scheduler_data: compare_schedulerUpdate):
    """
    Update a teacher code by code.
    """
    with Session(engine) as session:
        compare_scheduler = session.get(compare_scheduler, code)
        if not compare_scheduler:
            raise HTTPException(status_code=404, detail="Compare_scheduler not found")
        
        # Update only provided fields
        update_data = compare_scheduler_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(update_data, key, value)
        
        try:
            save_to_db(session, update_data)
            return update_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating compare_scheduler %s", code)
            raise HTTPException(
                status_code=409, detail=f"Error updating compare_scheduler with code '{code}'"
            ) from exc


@router.delete("/")
def delete_compare_scheduler():
    """
    Delete every compare_scheduler.
    """
    with Session(engine) as session:
        session.exec(delete(compare_scheduler))
        session.commit()
        
        return {"message": "All compare_scheduler entries deleted successfully"}
