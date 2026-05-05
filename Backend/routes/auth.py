from datetime import datetime, timedelta, timezone, date
from pydantic import BaseModel
from typing import Optional
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select
from config import settings
from database import engine
from models import Role, User, UserCreate, Room, EcoUserRoomParticipation, utc_now_naive
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.
    """
    to_encode = data.copy() # make a copy of the data to encode
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta # set expiration time
    else:
        expire = datetime.now(timezone.utc) + settings.access_token_expire_delta # default expiration
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM) # encode the token
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """
    Hash a plain password.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verify a JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        logger.warning("Token verification failed or token invalid")
        raise credentials_exception


def get_current_user(username: str = Depends(verify_token)):
    """
    Get the current user from the token.
    """
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == username)
        ).first() 
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user not found"
            )
        return user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(lambda: Session(engine)),
):
    """
    User login endpoint.
    """
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    if not user:
        logger.warning("Login failed: user not found '%s'", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ce compte n'existe pas. Veuillez créer un compte.",
        )

    if user.role == Role.GUEST:
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "role": user.role.value,
            "must_change_password": user.must_change_password
        }

    if not user.password_hash or not verify_password(form_data.password, user.password_hash):
        logger.warning("Login failed: invalid password for user '%s'", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        ) 

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role.value,
        "must_change_password": user.must_change_password
    } 


@router.post("/register/guest")
def register_guest(
    user_create: UserCreate,
    session: Session = Depends(lambda: Session(engine)),
):
    """
    Register a new guest user.
    """
    if not (8 <= len(user_create.username) <= 50):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom d'utilisateur doit comporter entre 8 et 50 caractères",
        )

    existing_user = session.exec(
        select(User).where(User.username == user_create.username)
    ).first()
    if existing_user:
        return {
            "success": False,
            "error": "Ce nom d'utilisateur existe déjà.",
        }

    # Validate room if provided
    selected_room_name = None
    if user_create.preferred_room_name:
        room = session.exec(
            select(Room).where(Room.name == user_create.preferred_room_name)
        ).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )
        selected_room_name = user_create.preferred_room_name

    new_user = User(
        username=user_create.username,
        password_hash="guest-account",
        role=Role.GUEST,
        must_change_password=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # If a room was selected, store it as a non-active preference.
    # The user will confirm this choice later from the "Ma Salle" page.
    if selected_room_name:
        from datetime import date, timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday of current week
        
        participation = EcoUserRoomParticipation(
            user_id=new_user.id,
            room_name=selected_room_name,
            week_start_date=week_start,
            joined_at=utc_now_naive(),
            is_active=False
        )
        session.add(participation)
        session.commit()

    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role.value}
    )

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "username": new_user.username,
        "role": new_user.role.value,
        "must_change_password": new_user.must_change_password
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    return {
        "username": current_user.username,
        "role": current_user.role.value
    }


@router.get("/protected")
def protected_route(username: str = Depends(verify_token)):
    """
    a protected route that requires authentication.
    """
    return {"message": f"welcome {username}"}


@router.get("/users/list")
def list_all_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(lambda: Session(engine)),
):
    """
    list all users in the system.

    restricted to users with the RESPONSABLE role. Password hashes are
    never returned.
    """
    if current_user.role.value != "RESPONSABLE":
        logger.warning(
            "Unauthorized users/list access attempt by '%s' (role=%s)",
            current_user.username,
            current_user.role.value,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="insufficient privileges",
        )

    users = session.exec(select(User)).all()
    return [
        {
            "id": user.id,
            "role": user.role.value,
        }
        for user in users
    ]

# Define Pydantic model for password change request, only way to read the json body
class PasswordCheckRequest(BaseModel):
    password: str

@router.post("/current-password-check")
def is_current_password_correct(
    request: PasswordCheckRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Check if the provided password matches the current user's password.
    """
    if verify_password(request.password, current_user.password_hash):
        return {"correct": True}
    else:
        return {"correct": False}