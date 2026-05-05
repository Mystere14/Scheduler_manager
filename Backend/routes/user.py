"""
Routes for managing Autonomous Systems (AS).
"""
# pylint: disable=invalid-name
from typing import List
from routes.auth import hash_password
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
import re # regex
from database import engine
from models import User, UserCreate, UserRead, UserUpdate, Role
from utils import save_to_db
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)
# Create User
@router.post("/", response_model=UserRead)
def create_user(user_data: UserCreate):
    """
    Create a new user.
    """
    new_user = User.model_validate(user_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_user)
            return new_user
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating user %s", user_data.username)
            raise HTTPException(
                status_code=409, detail=f"User with username '{user_data.username}' already exists"
            ) from exc


@router.get("/", response_model=List[UserRead])
def user_list():
    """
    Get all users.
    """
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users


@router.get("/{username}", response_model=UserRead)
def get_user(username: str):
    """
    Get a user by username.
    """
    with Session(engine) as session:
        user = session.get(User, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


# function to validate password strength even if already done in frontend
def validate_password_strength(password: str) -> str:
    """Retourne un message d'erreur ou None si valide"""
    if len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caractères"
    if not re.search(r"[A-Z]", password):
        return "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r"[a-z]", password):
        return "Le mot de passe doit contenir au moins une minuscule"
    if not re.search(r"\d", password):
        return "Le mot de passe doit contenir au moins un chiffre"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Le mot de passe doit contenir au moins un caractère spécial"
    if re.search(r"\s", password):
        return "Le mot de passe ne doit pas contenir d'espaces"
    return None


@router.put("/{username}", response_model=UserRead)
def update_user(username: str, user_data: UserUpdate):
    """
    Update a user.
    """
    if user_data.password :
        error = validate_password_strength(user_data.password)
        if error:
            raise HTTPException(status_code=400, detail=error)

    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == username)).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        if user_data.password:
            # Hash the new password
            hashed_password = hash_password(user_data.password)
            db_user.password_hash = hashed_password
            
        if user_data.must_change_password is not None:
            db_user.must_change_password = user_data.must_change_password
            
        if user_data.role:
            db_user.role = user_data.role
            
        save_to_db(session, db_user)
        
        return db_user


@router.delete("/{username}")
def delete_user(username: str): 
    """
    Delete a user.
    """
    with Session(engine) as session:
        user = session.get(User, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
        return {"detail": f"User '{username}' deleted successfully"}

