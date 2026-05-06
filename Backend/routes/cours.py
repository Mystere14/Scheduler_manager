import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import engine
from models import Cours, CoursCreate, CoursRead, CoursUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cours",
    tags=["cours"],
)


@router.get("/", response_model=List[CoursRead])
def get_cours():
    """
    Get all courses.
    """
    with Session(engine) as session:
        courses = session.exec(select(Cours)).all()
        return courses


@router.get("/teacher/{code_ens}", response_model=List[CoursRead])
def get_cours_by_teacher(code_ens: str):
    """
    Get every courses for a specific teacher.
    """
    with Session(engine) as session:
        courses = session.exec(
            select(Cours).where(Cours.code_ens == code_ens)
        ).all()
        if not courses:
            raise HTTPException(status_code=404, detail="No courses found for this teacher")
        return courses


@router.post("/", response_model=CoursRead)
def create_cours(cours_data: CoursCreate):
    """
    Create a new course.
    """
    new_cours = Cours.model_validate(cours_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_cours)
            return new_cours
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating cours %s", cours_data.code_res_sae)
            raise HTTPException(
                status_code=409, detail=f"Error creating course '{cours_data.code_res_sae}'"
            ) from exc


@router.put("/{cours_id}", response_model=CoursRead)
def update_cours(cours_id: int, cours_data: CoursUpdate):
    """
    Update a course by ID.
    """
    with Session(engine) as session:
        cours = session.get(Cours, cours_id)
        if not cours:
            raise HTTPException(status_code=404, detail="Cours not found")
        
        # Update only provided fields
        update_data = cours_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cours, key, value)
        
        try:
            save_to_db(session, cours)
            return cours
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating cours %s", cours_id)
            raise HTTPException(
                status_code=409, detail=f"Error updating course with ID '{cours_id}'"
            ) from exc


@router.delete("/{cours_id}")
def delete_cours(cours_id: int):
    """
    Delete a course by ID.
    """
    with Session(engine) as session:
        cours = session.get(Cours, cours_id)
        if not cours:
            raise HTTPException(status_code=404, detail="Cours not found")
        
        session.delete(cours)
        session.commit()
        
        return {"message": f"Course with ID {cours_id} deleted successfully"}
