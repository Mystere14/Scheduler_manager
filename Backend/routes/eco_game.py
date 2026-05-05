"""Eco-Salle game routes.

These endpoints expose the state for the "Ma Salle" game, including
user participation, quest completions and leaderboards, backed by the
SQL database instead of frontend cache/localStorage.
"""

import datetime
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import (
    Room,
    User,
    EcoUserRoomParticipation,
    EcoQuestCompletion,
    EcoQuestDefinition,
    EcoTaskReservation,
    EcoTaskReservationStatus,
)
from routes.auth import get_current_user

router = APIRouter(
    prefix="/eco",
    tags=["Eco-Salle (Ma Salle)"],
)


def _current_week_start(today: Optional[date] = None) -> date:
    """Return the Monday of the week for the given date.

    Weeks are considered from Monday (0) to Sunday (6).
    """

    if today is None:
        today = date.today()
    weekday = today.weekday()  # Monday=0
    return today - timedelta(days=weekday)


def _get_active_participation(
    session: Session, user: User, week_start: date
) -> Optional[EcoUserRoomParticipation]:
    return session.exec(
        select(EcoUserRoomParticipation)
        .where(EcoUserRoomParticipation.user_id == user.id)
        .where(EcoUserRoomParticipation.week_start_date == week_start)
        .where(EcoUserRoomParticipation.is_active == True)  # noqa: E712
    ).first()


def _get_latest_participation_room(
    session: Session, user: User
) -> Optional[Room]:
    """Return the latest room linked to the user from participation history."""

    latest_participation = session.exec(
        select(EcoUserRoomParticipation)
        .where(EcoUserRoomParticipation.user_id == user.id)
        .order_by(EcoUserRoomParticipation.joined_at.desc())
    ).first()

    if not latest_participation:
        return None

    return session.get(Room, latest_participation.room_name)


def _compute_user_and_room_points(
    session: Session, user: User, room_name: str, week_start: date
) -> dict:
    today = date.today()
    week_end = week_start + timedelta(days=6)

    # User daily points
    user_daily_points = session.exec(
        select(EcoQuestCompletion.points)
        .where(EcoQuestCompletion.user_id == user.id)
        .where(EcoQuestCompletion.room_name == room_name)
        .where(EcoQuestCompletion.event_date == today)
    ).all()
    user_daily_total = sum(user_daily_points) if user_daily_points else 0

    # User weekly points (current week)
    user_week_points = session.exec(
        select(EcoQuestCompletion.points)
        .where(EcoQuestCompletion.user_id == user.id)
        .where(EcoQuestCompletion.room_name == room_name)
        .where(EcoQuestCompletion.event_date >= week_start)
        .where(EcoQuestCompletion.event_date <= week_end)
    ).all()
    user_week_total = sum(user_week_points) if user_week_points else 0

    # Room daily points
    room_daily_points = session.exec(
        select(EcoQuestCompletion.points)
        .where(EcoQuestCompletion.room_name == room_name)
        .where(EcoQuestCompletion.event_date == today)
    ).all()
    room_daily_total = sum(room_daily_points) if room_daily_points else 0

    # Room weekly points
    room_week_points = session.exec(
        select(EcoQuestCompletion.points)
        .where(EcoQuestCompletion.room_name == room_name)
        .where(EcoQuestCompletion.event_date >= week_start)
        .where(EcoQuestCompletion.event_date <= week_end)
    ).all()
    room_week_total = sum(room_week_points) if room_week_points else 0

    return {
        "user_points": {"daily": user_daily_total, "weekly": user_week_total},
        "room_points": {"daily": room_daily_total, "weekly": room_week_total},
    }


@router.get("/my-room/state")
def get_my_room_state(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return the current Eco-Salle state for the authenticated user.

    This is the main entry point for the "Ma Salle" page: it exposes
    the room the user is associated with for the current week, their
    personal and room points, and the list of quest IDs already
    completed today.
    """

    week_start = _current_week_start()
    participation = _get_active_participation(session, current_user, week_start)
    preferred_room = _get_latest_participation_room(session, current_user)

    if not participation:
        return {
            "current_room": None,
            "preferred_room": {
                "name": preferred_room.name,
                "floor": preferred_room.floor,
                "size": preferred_room.size,
                "status": preferred_room.status,
            }
            if preferred_room
            else None,
            "week_start_date": week_start,
            "user_points": {"daily": 0, "weekly": 0},
            "room_points": {"daily": 0, "weekly": 0},
            "completed_quest_ids": [],
        }

    room = session.get(Room, participation.room_name)
    if not room:
        # Inconsistent state: participation references a missing room
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Associated room not found for current participation",
        )

    today = date.today()
    # User-level completed quests for today (used for quizz, etc.)
    completed_quests = session.exec(
        select(EcoQuestCompletion.quest_id)
        .where(EcoQuestCompletion.user_id == current_user.id)
        .where(EcoQuestCompletion.room_name == participation.room_name)
        .where(EcoQuestCompletion.event_date == today)
    ).all()

    # Room-level completed quests for today (any user in the room)
    room_completed_quests = session.exec(
        select(EcoQuestCompletion.quest_id)
        .where(EcoQuestCompletion.room_name == participation.room_name)
        .where(EcoQuestCompletion.event_date == today)
    ).all()

    # Active task reservations for today in this room
    reservation_rows = session.exec(
        select(EcoTaskReservation, User.username)
        .join(User, User.id == EcoTaskReservation.user_id)
        .where(EcoTaskReservation.room_name == participation.room_name)
        .where(EcoTaskReservation.event_date == today)
        .where(EcoTaskReservation.status == EcoTaskReservationStatus.RESERVED)
    ).all()

    task_reservations = [
        {"quest_id": res.quest_id, "username": username}
        for res, username in reservation_rows
    ]

    points = _compute_user_and_room_points(
        session, current_user, participation.room_name, week_start
    )

    return {
        "current_room": {
            "name": room.name,
            "floor": room.floor,
            "size": room.size,
            "status": room.status,
        },
        "preferred_room": {
            "name": preferred_room.name,
            "floor": preferred_room.floor,
            "size": preferred_room.size,
            "status": preferred_room.status,
        }
        if preferred_room
        else None,
        "week_start_date": week_start,
        **points,
        "completed_quest_ids": completed_quests or [],
        "room_completed_quest_ids": room_completed_quests or [],
        "task_reservations": task_reservations,
    }


class JoinRoomRequest(BaseModel):
    """Request body for joining a room.

    We keep only the room_name field from the participation model in the
    request; user and week are inferred from the authenticated context.
    """

    room_name: str


@router.post("/my-room/join")
def join_my_room(
    body: JoinRoomRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Associate the current user to a room for the current week.

    Enforces the rule "one room per user per week". If the user already
    has an active participation for this week in a different room, the
    request is rejected.
    """

    week_start = _current_week_start()

    # Validate room exists
    room = session.get(Room, body.room_name)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    existing = _get_active_participation(session, current_user, week_start)
    if existing:
        if existing.room_name == body.room_name:
            # Idempotent: already in this room
            points = _compute_user_and_room_points(
                session, current_user, existing.room_name, week_start
            )
            today = date.today()
            completed_quests = session.exec(
                select(EcoQuestCompletion.quest_id)
                .where(EcoQuestCompletion.user_id == current_user.id)
                .where(EcoQuestCompletion.room_name == existing.room_name)
                .where(EcoQuestCompletion.event_date == today)
            ).all()
            return {
                "current_room": {
                    "name": room.name,
                    "floor": room.floor,
                    "size": room.size,
                    "status": room.status,
                },
                "week_start_date": week_start,
                **points,
                "completed_quest_ids": completed_quests or [],
            }
        # Different room in same week: forbidden
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà choisi une salle pour cette semaine.",
        )

    participation = EcoUserRoomParticipation(
        user_id=current_user.id,
        room_name=body.room_name,
        week_start_date=week_start,
        is_active=True,
    )
    session.add(participation)
    session.commit()

    points = _compute_user_and_room_points(
        session, current_user, body.room_name, week_start
    )
    return {
        "current_room": {
            "name": room.name,
            "floor": room.floor,
            "size": room.size,
            "status": room.status,
        },
        "week_start_date": week_start,
        **points,
        "completed_quest_ids": [],
    }


@router.post("/my-room/leave")
def leave_my_room(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Allow the current user to leave their room for this week.

    This deactivates the current participation so the user can
    éventuellement choisir une autre salle. Les points déjà gagnés
    restent enregistrés dans l'historique.
    """

    week_start = _current_week_start()
    participation = _get_active_participation(session, current_user, week_start)
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune salle active à quitter pour cette semaine.",
        )

    participation.is_active = False
    participation.left_at = datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    )
    session.add(participation)
    session.commit()

    # Après avoir quitté, l'état est équivalent à un utilisateur sans salle
    return {
        "current_room": None,
        "week_start_date": week_start,
        "user_points": {"daily": 0, "weekly": 0},
        "room_points": {"daily": 0, "weekly": 0},
        "completed_quest_ids": [],
    }


class QuestCompletionRequest(BaseModel):
    """Body for quest/action completion.

    The frontend provides the quest_id and the number of points granted
    for this completion. The backend persists this event and recomputes
    the relevant scores.
    """

    quest_id: str
    points: int
    source: Optional[str] = None


class TaskReservationRequest(BaseModel):
    """Body for task reservation / unreservation requests."""

    quest_id: str


def _ensure_quest_definition(
    session: Session,
    quest_id: str,
    default_points: int = 0,
):
    """Create a minimal quest definition when the quest_id is dynamic."""

    quest_def = session.get(EcoQuestDefinition, quest_id)
    if quest_def:
        return quest_def

    quest_def = EcoQuestDefinition(
        id=quest_id,
        title=quest_id,
        base_points=default_points,
        category=None,
        is_room_level=True,
    )
    session.add(quest_def)
    session.commit()
    return quest_def


@router.post("/quests/complete")
def complete_quest(
    body: QuestCompletionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Record the completion of a quest/action for the current user.

    The user must be associated to a room for the current week. If the
    same quest_id has already been completed today by this user in this
    room, the call is idempotent and returns 0 added points.
    """

    if body.points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Points must be a positive integer",
        )

    week_start = _current_week_start()
    participation = _get_active_participation(session, current_user, week_start)
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez d'abord rejoindre une salle pour participer.",
        )

    today = date.today()

    # Ensure quest definition exists
    _ensure_quest_definition(session, body.quest_id, default_points=body.points)

    # Daily actions are room-level: one validation per room/day.
    if body.source == "DAILY_ACTION":
        room_already_completed = session.exec(
            select(EcoQuestCompletion)
            .where(EcoQuestCompletion.room_name == participation.room_name)
            .where(EcoQuestCompletion.quest_id == body.quest_id)
            .where(EcoQuestCompletion.event_date == today)
        ).first()
        if room_already_completed:
            points = _compute_user_and_room_points(
                session, current_user, participation.room_name, week_start
            )
            return {
                "added_points": 0,
                **points,
            }

        # For daily actions, only the user that reserved the task can validate it.
        reservation = session.exec(
            select(EcoTaskReservation)
            .where(EcoTaskReservation.user_id == current_user.id)
            .where(EcoTaskReservation.room_name == participation.room_name)
            .where(EcoTaskReservation.quest_id == body.quest_id)
            .where(EcoTaskReservation.event_date == today)
            .where(EcoTaskReservation.status == EcoTaskReservationStatus.RESERVED)
        ).first()
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cette action doit d'abord être assignée avant validation.",
            )

    # Idempotency: prevent completing the same quest more than once per day
    existing = session.exec(
        select(EcoQuestCompletion)
        .where(EcoQuestCompletion.user_id == current_user.id)
        .where(EcoQuestCompletion.room_name == participation.room_name)
        .where(EcoQuestCompletion.quest_id == body.quest_id)
        .where(EcoQuestCompletion.event_date == today)
    ).first()
    if existing:
        points = _compute_user_and_room_points(
            session, current_user, participation.room_name, week_start
        )
        return {
            "added_points": 0,
            **points,
        }

    completion = EcoQuestCompletion(
        user_id=current_user.id,
        room_name=participation.room_name,
        quest_id=body.quest_id,
        event_date=today,
        points=body.points,
        source=body.source,
    )
    session.add(completion)

    # Marquer une éventuelle réservation correspondante comme complétée
    reservation = session.exec(
        select(EcoTaskReservation)
        .where(EcoTaskReservation.user_id == current_user.id)
        .where(EcoTaskReservation.room_name == participation.room_name)
        .where(EcoTaskReservation.quest_id == body.quest_id)
        .where(EcoTaskReservation.event_date == today)
        .where(EcoTaskReservation.status == EcoTaskReservationStatus.RESERVED)
    ).first()
    if reservation:
        reservation.status = EcoTaskReservationStatus.COMPLETED
        reservation.completed_at = datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=None
        )
        session.add(reservation)

    session.commit()

    points = _compute_user_and_room_points(
        session, current_user, participation.room_name, week_start
    )
    return {
        "added_points": body.points,
        **points,
    }


@router.post("/tasks/reserve")
def reserve_task(
    body: TaskReservationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Reserve a daily task (quest) for the current user.

    Only one active reservation is allowed per room/quest/day. If another
    user has already reserved it, a 409 error is returned.
    """

    week_start = _current_week_start()
    participation = _get_active_participation(session, current_user, week_start)
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez d'abord rejoindre une salle pour participer.",
        )

    today = date.today()

    # Ensure quest definition exists for dynamic daily-action quest IDs
    _ensure_quest_definition(session, body.quest_id)

    existing = session.exec(
        select(EcoTaskReservation)
        .where(EcoTaskReservation.room_name == participation.room_name)
        .where(EcoTaskReservation.quest_id == body.quest_id)
        .where(EcoTaskReservation.event_date == today)
        .where(EcoTaskReservation.status == EcoTaskReservationStatus.RESERVED)
    ).first()

    if existing and existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette tâche est déjà assignée à un autre joueur.",
        )

    if not existing:
        reservation = EcoTaskReservation(
            user_id=current_user.id,
            room_name=participation.room_name,
            quest_id=body.quest_id,
            event_date=today,
            status=EcoTaskReservationStatus.RESERVED,
        )
        session.add(reservation)
        session.commit()

    # Retourner l'état Eco-Salle à jour
    return get_my_room_state(current_user=current_user, session=session)


@router.post("/tasks/release")
def release_task(
    body: TaskReservationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Release a previously reserved task for the current user."""

    week_start = _current_week_start()
    participation = _get_active_participation(session, current_user, week_start)
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez d'abord rejoindre une salle pour participer.",
        )

    today = date.today()
    reservation = session.exec(
        select(EcoTaskReservation)
        .where(EcoTaskReservation.room_name == participation.room_name)
        .where(EcoTaskReservation.quest_id == body.quest_id)
        .where(EcoTaskReservation.event_date == today)
        .where(EcoTaskReservation.user_id == current_user.id)
        .where(EcoTaskReservation.status == EcoTaskReservationStatus.RESERVED)
    ).first()

    if reservation:
        reservation.status = EcoTaskReservationStatus.CANCELLED
        reservation.expires_at = datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=None
        )
        session.add(reservation)
        session.commit()

    return get_my_room_state(current_user=current_user, session=session)


@router.get("/leaderboard")
def get_leaderboard(session: Session = Depends(get_session)):
    """Return the current leaderboard for Eco-Salle.

    Ranks rooms by their daily points (then weekly total as tie breaker)
    for the current week. Only rooms in Experimentation status are
    included to match the Ma Salle game context.
    """

    from models import Status, EcoUserRoomParticipation as Participation

    today = date.today()
    week_start = _current_week_start(today)
    week_end = week_start + timedelta(days=6)

    rooms = session.exec(
        select(Room).where(Room.status == Status.Experimentation)
    ).all()

    # Preload completions and participations for the week
    completions = session.exec(
        select(EcoQuestCompletion)
        .where(EcoQuestCompletion.event_date >= week_start)
        .where(EcoQuestCompletion.event_date <= week_end)
    ).all()

    participations = session.exec(
        select(Participation)
        .where(Participation.week_start_date == week_start)
        .where(Participation.is_active == True)  # noqa: E712
    ).all()

    # Aggregate scores by room
    daily_scores = {room.name: 0 for room in rooms}
    weekly_scores = {room.name: 0 for room in rooms}
    members = {room.name: 0 for room in rooms}

    for comp in completions:
        if comp.room_name not in weekly_scores:
            continue
        weekly_scores[comp.room_name] += comp.points
        if comp.event_date == today:
            daily_scores[comp.room_name] += comp.points

    for part in participations:
        if part.room_name in members:
            members[part.room_name] += 1

    leaderboard = []
    for room in rooms:
        leaderboard.append(
            {
                "roomId": room.name,
                "roomName": room.name,
                "dailyPoints": daily_scores.get(room.name, 0),
                "totalPoints": weekly_scores.get(room.name, 0),
                "members": max(1, members.get(room.name, 0)) if weekly_scores.get(room.name, 0) > 0 else members.get(room.name, 0),
            }
        )

    # Sort and compute ranks based on dailyPoints then totalPoints
    leaderboard.sort(
        key=lambda r: (r["dailyPoints"], r["totalPoints"]),
        reverse=True,
    )

    for idx, item in enumerate(leaderboard, start=1):
        item["rank"] = idx

    return leaderboard