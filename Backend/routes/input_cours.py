import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import engine
from models import Input_cours, Input_coursCreate, Input_coursRead, Input_coursUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/input_cours",
    tags=["input_cours"],
)


@router.get("/", response_model=List[Input_coursRead])
def get_input_cours():
    """
    Get all input courses.
    """
    with Session(engine) as session:
        courses = session.exec(select(Input_cours)).all()
        return courses

@router.post("/", response_model=Input_coursRead)
def create_input_cours(input_cours_data: Input_coursCreate):
    """
    Create a new input course.
    """
    new_input_cours = Input_cours.model_validate(input_cours_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_input_cours)
            return new_input_cours
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating input course %s", input_cours_data.code_res_sae)
            raise HTTPException(
                status_code=409, detail=f"Error creating course '{input_cours_data.code_res_sae}'"
            ) from exc


@router.put("/{input_cours_id}", response_model=Input_coursRead)
def update_input_cours(input_cours_id: int, input_cours_data: Input_coursUpdate):
    """
    Update an input course by ID.
    """
    with Session(engine) as session:
        input_cours = session.get(Input_cours, input_cours_id)
        if not input_cours:
            raise HTTPException(status_code=404, detail="Input course not found")
        
        # Update only provided fields
        update_data = input_cours_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(input_cours, key, value)
        
        try:
            save_to_db(session, input_cours)
            return input_cours
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating input course %s", input_cours_id)
            raise HTTPException(
                status_code=409, detail=f"Error updating course with ID '{input_cours_id}'"
            ) from exc


@router.delete("/{input_cours_id}")
def delete_input_cours(input_cours_id: int):
    """
    Delete an input course by ID.
    """
    with Session(engine) as session:
        input_cours = session.get(Input_cours, input_cours_id)
        if not input_cours:
            raise HTTPException(status_code=404, detail="Input course not found")
        
        session.delete(input_cours)
        session.commit()
        
        return {"message": f"Course with ID {input_cours_id} deleted successfully"}

@router.delete("/")
def delete_input_cours():
    """
    Delete every input courses.
    """
    with Session(engine) as session:
        input_cours = session.exec(select(Input_cours)).all()

        if not input_cours:
            raise HTTPException(
                status_code=404,
                detail="Input course not found"
            )

        for cours in input_cours:
            session.delete(cours)

        session.commit()

        return {
            "message": "Every input course deleted successfully"
        }