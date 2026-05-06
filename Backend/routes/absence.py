import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import engine
from models import Absence, AbsenceCreate, AbsenceRead, AbsenceUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/absences",
    tags=["absences"],
)

@router.get("/teacher/{teacher}", response_model=List[AbsenceRead])
def get_absences_by_teacher(teacher: str):
    """
    Get all absences for a specific teacher.
    """
    with Session(engine) as session:
        absences = session.exec(
            select(Absence).where(Absence.enseignant == teacher)
        ).all()
        if not absences:
            raise HTTPException(status_code=404, detail="No absences found for this teacher")
        return absences


@router.post("/", response_model=AbsenceRead)
def create_absence(absence_data: AbsenceCreate):
    """
    Create a new absence.
    """
    new_absence = Absence.model_validate(absence_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_absence)
            return new_absence
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating absence for teacher %s", absence_data.enseignant)
            raise HTTPException(
                status_code=409, detail=f"Error creating absence for teacher '{absence_data.enseignant}'"
            ) from exc


@router.put("/{absence_id}", response_model=AbsenceRead)
def update_absence(absence_id: int, absence_data: AbsenceUpdate):
    """
    Update an absence by ID.
    """
    with Session(engine) as session:
        absence = session.get(Absence, absence_id)
        if not absence:
            raise HTTPException(status_code=404, detail="Absence not found")
        
        # Update only provided fields
        update_data = absence_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(absence, key, value)
        
        try:
            save_to_db(session, absence)
            return absence
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating absence %s", absence_id)
            raise HTTPException(
                status_code=409, detail=f"Error updating absence with ID '{absence_id}'"
            ) from exc


@router.delete("/{absence_id}")
def delete_absence(absence_id: int):
    """
    Delete an absence by ID.
    """
    with Session(engine) as session:
        absence = session.get(Absence, absence_id)
        if not absence:
            raise HTTPException(status_code=404, detail="Absence not found")
        
        session.delete(absence)
        session.commit()
        
        return {"message": f"Absence with ID {absence_id} deleted successfully"}



