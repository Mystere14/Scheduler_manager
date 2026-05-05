"""
Routes for managing Rooms.
"""
from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Body, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, func

from database import engine, get_session
from models import AcquisitionSystem, Room, RoomCreate, RoomRead, RoomUpdate, Status, State, Notification
from utils import save_to_db, get_or_404
from services.limiter import limiter, get_ip
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rooms",
    tags=["Salles (Rooms)"],
)


@router.post("/", response_model=RoomRead)
def create_room(room: RoomCreate, session: Session = Depends(get_session)):
    """
    Create a new Room.
    """
    new_room = Room.model_validate(room)
    try:
        save_to_db(session, new_room)
        return new_room
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"Room with name '{room.name}' already exists"
        ) from exc


@router.post("/{room_name}/link/{acquisition_system_name}", response_model=RoomRead)
def link_room_to_acquisition_system(room_name: str, acquisition_system_name: str, session: Session = Depends(get_session)):
    """
    Link a Room to an Acquisition System (AcquisitionSystem).
    """
    existing_room = get_or_404(session, Room, room_name, "Room not found")

    # Check if room already has an AcquisitionSystem linked
    current_linked = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    if current_linked:
        raise HTTPException(status_code=400, detail="Room already has an AcquisitionSystem linked. Unlink it first.")

    existing_acquisition_system = get_or_404(session, AcquisitionSystem, acquisition_system_name, "AcquisitionSystem not found")

    # Prevent linking an AcquisitionSystem that's already assigned to another room
    if existing_acquisition_system.room_name and existing_acquisition_system.room_name != room_name:
        raise HTTPException(status_code=400, detail="AcquisitionSystem is already linked to another room")

    # Update relationship
    existing_acquisition_system.room_name = room_name
    
    # Automatically update status to Installation when linking SA to Room
    # regardless of IP (IP will be configured by technician later)
    existing_room.status = Status.Installation
    existing_acquisition_system.status = Status.Installation
    if existing_acquisition_system.addressIP:
        existing_acquisition_system.ASState = State.Connected

    session.add(existing_acquisition_system)
    save_to_db(session, existing_room)
    
    # Populate linked_acquisition_systems for response
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read




@router.get("/", response_model=List[RoomRead])
def room_list(session: Session = Depends(get_session)):
    """
    Get all Rooms.
    """
    rooms = session.exec(select(Room)).all()
    # We might want to populate linked_acquisition_systems for all rooms, but it might be slow.
    # For now, let's return basic room info.
    return rooms


@router.get("/{name}", response_model=RoomRead)
def get_room(name: str, session: Session = Depends(get_session)):
    """
    Get a Room by name.
    """
    existing_room = get_or_404(session, Room, name, "Room not found")
    
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.put("/{name}", response_model=RoomRead)
def update_room(name: str, room_update: RoomUpdate, session: Session = Depends(get_session)):
    """
    Update a Room.
    """
    existing_room = get_or_404(session, Room, name, "Room not found")
    room_data = room_update.model_dump(exclude_unset=True)
    for key, value in room_data.items():
        setattr(existing_room, key, value)
    save_to_db(session, existing_room)
    
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.delete("/{name}")
def delete_room(name: str, session: Session = Depends(get_session)):
    """
    Delete a Room.
    """
    existing_room = get_or_404(session, Room, name, "Room not found")
    
    # Unlink AcquisitionSystems
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == name)).all()
    for acquisition_system_item in linked_acquisition_systems:
        acquisition_system_item.room_name = None
        acquisition_system_item.status = Status.Register
        acquisition_system_item.ASState = State.Connected
        session.add(acquisition_system_item)

    # Delete associated captures
    from models import Capture
    captures = session.exec(select(Capture).where(Capture.roomName == name)).all()
    for capture in captures:
        session.delete(capture)

    # Delete associated notifications (feedback/likes/dislikes)
    notifications = session.exec(select(Notification).where(Notification.room_name == name)).all()
    for notification in notifications:
        session.delete(notification)

    session.delete(existing_room)
    session.commit()
    return {"detail": "Room deleted successfully"}


@router.get("/status/{status}", response_model=List[RoomRead])
def get_rooms_by_status(status: str, session: Session = Depends(get_session)):
    """
    Get Rooms by status.
    """
    rooms = session.exec(select(Room).where(Room.status == status)).all()
    
    result = []
    for room in rooms: # loop through rooms to populate linked_acquisition_systems
        linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room.name)).all()
        room_read = RoomRead.model_validate(room)
        room_read.linked_acquisition_systems = linked_acquisition_systems
        result.append(room_read)
        
    return result


@router.post("/{room_name}/unlink/{acquisition_system_name}", response_model=RoomRead)
def unlink_acquisition_system_from_room(room_name: str, acquisition_system_name: str, session: Session = Depends(get_session)):
    """
    Unlink an Acquisition System (AcquisitionSystem) from a Room.
    """
    existing_room = get_or_404(session, Room, room_name, "Room not found")

    existing_acquisition_system = get_or_404(session, AcquisitionSystem, acquisition_system_name, "AcquisitionSystem not found")

    if existing_acquisition_system.room_name != room_name:
            raise HTTPException(status_code=400, detail="AcquisitionSystem is not linked to this room")

    # Update relationship
    existing_acquisition_system.room_name = None
    existing_acquisition_system.status = Status.Register
    existing_acquisition_system.ASState = State.Connected # Or keep as is? Resetting to Connected seems safer.

    session.add(existing_acquisition_system)
    session.commit()
    session.refresh(existing_room)
    
    # Check if there are any other AcquisitionSystem linked to this room
    remaining_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    if not remaining_acquisition_systems:
        existing_room.status = Status.Register
        save_to_db(session, existing_room)
    
    # Populate linked_acquisition_systems for response
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.post("/{room_name}/like", response_model=RoomRead)
@limiter.shared_limit("1/hour", scope="room-reactions")
def like_room(request: Request, room_name: str, session: Session = Depends(get_session)):
    """
    Increment the like count for a room.
    """
    existing_room = get_or_404(session, Room, room_name, "Room not found")
    existing_room.like += 1
    save_to_db(session, existing_room)
    
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.post("/{room_name}/dislike", response_model=RoomRead)
@limiter.shared_limit("1/hour", scope="room-reactions")
def dislike_room(request: Request, room_name: str, session: Session = Depends(get_session)):
    """
    Increment the dislike count for a room.
    """
    existing_room = get_or_404(session, Room, room_name, "Room not found")
    existing_room.dislike += 1
    save_to_db(session, existing_room)
    
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.delete("/{room_name}/like", response_model=RoomRead)
def unlike_room(room_name: str, session: Session = Depends(get_session)):
    """
    Decrement the like count for a room (minimum 0).
    """
    existing_room = get_or_404(session, Room, room_name, "Room not found")
    existing_room.like = max(0, existing_room.like - 1)
    save_to_db(session, existing_room)
    
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.delete("/{room_name}/dislike", response_model=RoomRead)
def remove_dislike_room(room_name: str, session: Session = Depends(get_session)):
    """
    Decrement the dislike count for a room (minimum 0).
    """
    existing_room = get_or_404(session, Room, room_name, "Room not found")
    existing_room.dislike = max(0, existing_room.dislike - 1)
    save_to_db(session, existing_room)
    
    linked_acquisition_systems = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).all()
    room_read = RoomRead.model_validate(existing_room)
    room_read.linked_acquisition_systems = linked_acquisition_systems
    return room_read


@router.get("/{room_name}/feedback-status")
def get_feedback_status(room_name: str, request: Request, session: Session = Depends(get_session)):
    """
    Check if the user has given feedback for a room recently.
    """
    user_ip = get_ip(request)
    
    # Check for recent feedback for THIS room (likes/dislikes are stored as notifications)
    three_hours_ago = datetime.utcnow() - timedelta(hours=3)
    
    recent_feedback = session.exec(
        select(Notification)
        .where(Notification.room_name == room_name)
        .where(Notification.ip_address == user_ip)
        .where(Notification.sent_at >= three_hours_ago)
        .where((Notification.message == "like") | (Notification.message == "dislike"))
    ).first()
    
    # Check for rate limit: 3/hour across ALL rooms
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    hourly_feedback_count = session.exec(
        select(func.count(Notification.id))
        .where(Notification.ip_address == user_ip)
        .where(Notification.sent_at >= one_hour_ago)
        .where((Notification.message == "like") | (Notification.message == "dislike"))
    ).one()
    
    return {
        "has_given_feedback": recent_feedback is not None,
        "limit_reached": hourly_feedback_count >= 3
    }