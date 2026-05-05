import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from database import get_session
from models import Notification, NotificationRead, NotificationCreate, User, Role
from routes.auth import get_current_user
from services.limiter import limiter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationRead])
def get_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all notifications (Manager only).
    """
    if current_user.role != Role.RESPONSABLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le responsable peut consulter les notifications"
        )
    notifications = session.exec(select(Notification)).all()
    return notifications

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification (Manager only).
    """
    if current_user.role != Role.RESPONSABLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le responsable peut supprimer les notifications"
        )
        
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification introuvable")
        
    session.delete(notification)
    session.commit()
    return {"ok": True}

@router.post("/", response_model=NotificationRead)
@limiter.limit("3/hour")
def create_notification(
    request: Request,
    notification: NotificationCreate,
    session: Session = Depends(get_session)
):
    """
    Create a notification (Public access for non-connected users).
    """
    sender_name = notification.sender_name.strip()
    message = notification.message.strip()

    if not sender_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom de l'expéditeur est obligatoire"
        )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le message est obligatoire"
        )

    db_notification = Notification(
        sender_name=sender_name,
        message=message,
        room_name=notification.room_name,
    )
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification
