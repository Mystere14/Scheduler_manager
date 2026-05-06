import logging
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import engine
from models import Code_ens, Code_ensCreate, Code_ensRead, Code_ensUpdate
from utils import save_to_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/code_ens",
    tags=["code_ens"],
)


@router.get("/", response_model=List[Code_ensRead])
def list_code_ens():
    """
    Get all teacher codes.
    """
    with Session(engine) as session:
        codes = session.exec(select(Code_ens)).all()
        return codes


@router.get("/{code}", response_model=Code_ensRead)
def get_code_ens(code: str):
    """
    Get a teacher code by code.
    """
    with Session(engine) as session:
        code_ens = session.get(Code_ens, code)
        if not code_ens:
            raise HTTPException(status_code=404, detail="Code_ens not found")
        return code_ens


@router.post("/", response_model=Code_ensRead)
def create_code_ens(code_ens_data: Code_ensCreate):
    """
    Create a new teacher code.
    """
    new_code_ens = Code_ens.model_validate(code_ens_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_code_ens)
            return new_code_ens
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating code_ens %s", code_ens_data.code)
            raise HTTPException(
                status_code=409, detail=f"Code_ens with code '{code_ens_data.code}' already exists"
            ) from exc


@router.put("/{code}", response_model=Code_ensRead)
def update_code_ens(code: str, code_ens_data: Code_ensUpdate):
    """
    Update a teacher code by code.
    """
    with Session(engine) as session:
        code_ens = session.get(Code_ens, code)
        if not code_ens:
            raise HTTPException(status_code=404, detail="Code_ens not found")
        
        # Update only provided fields
        update_data = code_ens_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(code_ens, key, value)
        
        try:
            save_to_db(session, code_ens)
            return code_ens
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating code_ens %s", code)
            raise HTTPException(
                status_code=409, detail=f"Error updating code_ens with code '{code}'"
            ) from exc


@router.delete("/{code}")
def delete_code_ens(code: str):
    """
    Delete a teacher code by code.
    """
    with Session(engine) as session:
        code_ens = session.get(Code_ens, code)
        if not code_ens:
            raise HTTPException(status_code=404, detail="Code_ens not found")
        
        session.delete(code_ens)
        session.commit()
        
        return {"message": f"Code_ens with code '{code}' deleted successfully"}
