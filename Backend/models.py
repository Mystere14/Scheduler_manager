"""
Data models for the application.
"""
import datetime
from datetime import date
from enum import Enum
from typing import Optional


from pydantic import constr, BaseModel
from sqlmodel import Field, SQLModel
from typing import List

import datetime as _dt


def utc_now_naive() -> datetime.datetime:
    """Return UTC now as naive datetime for timestamp columns without tz."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


class Orientation(str, Enum):
    """
    Enum for room orientation.
    """
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    NORTHEAST = "Northeast"
    NORTHWEST = "Northwest"
    SOUTHEAST = "Southeast"
    SOUTHWEST = "Southwest"


class State(str, Enum):
    """
    Enum for AS state.
    """
    # pylint: disable=invalid-name
    Offline = "Offline"
    Connected = "Connected"
    Anomaly = "Anomaly"
    Warning = "Warning"
    AwaitingInstallation = "AwaitingInstallation"
    NotConfigured = "NotConfigured"


class Status(str, Enum):
    """
    Enum for AS/Room status.
    """
    # pylint: disable=invalid-name
    Experimentation = "Experimentation"
    Installation = "Installation"
    Register = "Register"

class Role(str, Enum):
    """
    Enum for User roles.
    """
    # pylint: disable=invalid-name
    RESPONSABLE = "RESPONSABLE"
    TECHNICIEN = "TECHNICIEN"
    GUEST = "GUEST"

class AcquisitionSystem(SQLModel, table=True):
    """
    Model for Acquisition Systems (AcquisitionSystem).
    """
    __tablename__ = "acquisition_systems"
    name: str = Field(primary_key=True, min_length=1, max_length=50)
    ASState: Optional[State] = Field(default=None)
    temperature: Optional[float] = Field(default=None)
    humidity: Optional[float] = Field(default=None)
    co2: Optional[float] = Field(default=None)
    tvoc: Optional[float] = Field(default=None)
    addressIP: Optional[constr(min_length=7, max_length=15)] = None
    activationDate: Optional[date] = None
    sensor: bool = Field(default=False)
    status: Status = Field(default=Status.Register)
    
    dht22_status: Optional[bool] = Field(default=None)
    sgp30_status: Optional[bool] = Field(default=None)
    oled_status: Optional[bool] = Field(default=None)
    last_forced_update: Optional[datetime.datetime] = Field(default=None)
    
    room_name: Optional[str] = Field(default=None, foreign_key="room.name")


class AcquisitionSystemCreate(SQLModel):
    """
    Model for creating an AcquisitionSystem.
    """
    name: constr(min_length=1, max_length=50)
    addressIP: Optional[constr(min_length=7, max_length=15)] = None


class AcquisitionSystemUpdate(SQLModel):
    """
    Model for updating an AcquisitionSystem.
    """
    ASState: Optional[State] = None
    addressIP: Optional[constr(min_length=7, max_length=15)] = None
    activationDate: Optional[date] = None
    sensor: Optional[bool] = None
    status: Optional[Status] = None
    room_name: Optional[str] = None
    dht22_status: Optional[bool] = None
    sgp30_status: Optional[bool] = None
    oled_status: Optional[bool] = None


class AcquisitionSystemRead(SQLModel):
    """
    Model for reading an AcquisitionSystem.
    """
    name: constr(min_length=1, max_length=50)
    ASState: Optional[State] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2: Optional[float] = None
    tvoc: Optional[float] = None
    addressIP: Optional[constr(min_length=7, max_length=15)] = None
    activationDate: Optional[date] = None
    sensor: bool
    status: Status
    room_name: Optional[str] = None
    dht22_status: Optional[bool] = None
    sgp30_status: Optional[bool] = None
    oled_status: Optional[bool] = None
    last_forced_update: Optional[datetime.datetime] = None


class Room(SQLModel, table=True):
    """
    Model for Rooms.
    """
    name: str = Field(primary_key=True, min_length=1, max_length=50)
    floor: int = Field(default=0, ge=-10, le=100)
    size: int = Field(default=0, ge=0)
    window: int = Field(default=0, ge=0)
    engines: int = Field(default=0, ge=0)
    door: int = Field(default=0, ge=0)
    orientation: Orientation
    description: Optional[constr(max_length=250)] = None
    status: Status = Field(default=Status.Register)
    like:int = Field(default=0, ge=0)
    dislike:int = Field(default=0, ge=0)


class RoomCreate(SQLModel):
    """
    Model for creating a Room.
    """
    name: constr(min_length=1, max_length=50)
    floor: int = Field(default=0, ge=-10, le=100)
    size: int = Field(default=0, ge=0)
    window: int = Field(default=0, ge=0)
    engines: int = Field(default=0, ge=0)
    door: int = Field(default=0, ge=0)
    orientation: Orientation
    description: Optional[constr(max_length=250)] = None


class RoomUpdate(SQLModel):
    """
    Model for updating a Room.
    """
    floor: Optional[int] = Field(default=None, ge=-10, le=100)
    size: Optional[int] = Field(default=None, ge=0)
    window: Optional[int] = Field(default=None, ge=0)
    engines: Optional[int] = Field(default=None, ge=0)
    door: Optional[int] = Field(default=None, ge=0)
    orientation: Optional[Orientation] = None
    description: Optional[constr(max_length=250)] = None
    status: Optional[Status] = None
    like: Optional[int] = Field(default=None, ge=0)
    dislike: Optional[int] = Field(default=None, ge=0)


class RoomRead(SQLModel):
    """
    Model for reading a Room.
    """
    name: constr(min_length=1, max_length=50)
    floor: int
    size: int
    window: int
    engines: int
    door: int
    orientation: Orientation
    description: Optional[constr(max_length=250)] = None
    status: Status
    like: int = Field(default=0, ge=0)
    dislike: int = Field(default=0, ge=0)
    # We will inject this manually in the route
    linked_acquisition_systems: Optional[list[AcquisitionSystemRead]] = None

# 
class Capture(SQLModel, table=True):
    """
    Model for Captures.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    temperature: float
    humidity: float
    co2: float
    tvoc: float
    dateCapture: datetime.datetime = Field(default_factory=datetime.datetime.now)

    roomName: constr(min_length=1, max_length=50) = Field(foreign_key="room.name")
    acquisition_system_name: Optional[constr(min_length=1, max_length=50)] = Field(
        default=None, foreign_key="acquisition_systems.name"
    )


class CaptureCreate(SQLModel):
    """
    Model for creating a Capture.
    """
    temperature: float
    humidity: float
    co2: float
    tvoc: float
    roomName: constr(min_length=1, max_length=50)
    acquisition_system_name: Optional[constr(min_length=1, max_length=50)] = None


class CaptureRead(SQLModel):
    """
    Model for reading a Capture.
    """
    id: int
    temperature: float
    humidity: float
    co2: float
    tvoc: float
    dateCapture: datetime.datetime
    roomName: constr(min_length=1, max_length=50)
    acquisition_system_name: Optional[constr(min_length=1, max_length=50)] = None

class SensorStatus(BaseModel):
    """
    Model for sensor status from IoT device.
    """
    dht22: Optional[bool] = None
    sgp30: Optional[bool] = None
    oled: Optional[bool] = None


class CaptureIoT(SQLModel):
    """
    Model for receiving data from IoT devices.
    """
    ip: str
    temperature: float
    humidity: float
    co2: float
    tvoc: float
    sensor_status: Optional[SensorStatus] = None
    forced_send: Optional[bool] = None


class User(SQLModel, table=True):
    """
    Model for Users.
    """
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    password_hash: Optional[str] = None
    role: Role
    created_at: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.now)
    must_change_password: bool = Field(default=True)


class UserCreate(SQLModel):
    """
    Model for creating a User.
    """
    username: str = Field(min_length=3, max_length=50)
    password: Optional[str] = Field(default=None, min_length=8)
    role: Role = Field()
    preferred_room_name: Optional[str] = Field(default=None)

class UserRead(SQLModel):
    """
    Model for reading a User.
    """
    id: int
    username: str
    role: Role
    created_at: datetime.datetime
    must_change_password: bool

class UserUpdate(SQLModel):
    """
    Model for updating a User.
    """
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    password: Optional[str] = Field(default=None, min_length=8)
    role: Optional[Role] = None
    must_change_password: Optional[bool] = None


class Notification(SQLModel, table=True):
    """
    Model for Notifications.
    """
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_name: str
    message: str
    sent_date: datetime.date = Field(default_factory=datetime.date.today)
    sent_at: datetime.datetime = Field(default_factory=utc_now_naive, index=True)
    room_name: str = Field(foreign_key="room.name")
    ip_address: Optional[str] = Field(default=None, index=True)


class NotificationRead(SQLModel):
    """
    Model for reading Notification data.
    """
    id: int
    sender_name: str
    message: str
    sent_date: datetime.date
    sent_at: datetime.datetime
    room_name: str
    ip_address: Optional[str] = None


class NotificationCreate(SQLModel):
    """
    Model for creating a Notification.
    """
    sender_name: str
    message: str
    room_name: str



class EcoUserRoomParticipation(SQLModel, table=True):
    """User participation in an Eco-Salle room for a given week.

    This table enforces the constraint "one room per user per week" and
    is the backbone for computing members per room and weekly rankings.
    """

    __tablename__ = "eco_user_room_participation"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    room_name: str = Field(foreign_key="room.name", index=True)
    week_start_date: date = Field(index=True)
    joined_at: datetime.datetime = Field(default_factory=utc_now_naive)
    left_at: Optional[datetime.datetime] = Field(default=None)
    is_active: bool = Field(default=True, index=True)


class EcoQuestDefinition(SQLModel, table=True):
    """Definition of a quest/action in the Eco-Salle game.

    This separates the description and base configuration of a quest
    from individual user completions.
    """

    __tablename__ = "eco_quest_definition"

    id: str = Field(primary_key=True, min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    base_points: int = Field(default=0, ge=0)
    category: Optional[str] = Field(default=None, index=True, max_length=50)
    is_room_level: bool = Field(default=True)
    repeat_per_day: bool = Field(default=False)
    repeat_per_week: bool = Field(default=False)


class EcoQuestCompletion(SQLModel, table=True):
    """Individual completion of a quest/action by a user in a room.

    These rows are the source of truth for user and room points and
    are used to compute daily/weekly scores and leaderboards.
    """

    __tablename__ = "eco_quest_completion"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    room_name: str = Field(foreign_key="room.name", index=True)
    quest_id: str = Field(foreign_key="eco_quest_definition.id", index=True)
    event_date: date = Field(default_factory=date.today, index=True)
    points: int = Field(ge=0)
    source: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime.datetime = Field(default_factory=utc_now_naive, index=True)


class EcoTaskReservationStatus(str, Enum):
    """Status for a reserved task/quest."""

    RESERVED = "reserved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class EcoTaskReservation(SQLModel, table=True):
    """Reservation/lock of a quest by a specific user in a room.

    Used so that other users can see a task is in progress and cannot
    take it simultaneously.
    """

    __tablename__ = "eco_task_reservation"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    room_name: str = Field(foreign_key="room.name", index=True)
    quest_id: str = Field(foreign_key="eco_quest_definition.id", index=True)
    event_date: date = Field(default_factory=date.today, index=True)
    status: EcoTaskReservationStatus = Field(default=EcoTaskReservationStatus.RESERVED)
    reserved_at: datetime.datetime = Field(default_factory=utc_now_naive)
    completed_at: Optional[datetime.datetime] = Field(default=None)
    expires_at: Optional[datetime.datetime] = Field(default=None)


class EcoRoomDailyMetrics(SQLModel, table=True):
    """Aggregated daily metrics for a room used by Niorty.

    Tracks how many minutes per day a room stays within "optimal" ranges
    for each metric (temperature, humidity, CO2, TVOC).
    """

    __tablename__ = "eco_room_daily_metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    room_name: str = Field(foreign_key="room.name", index=True)
    metric_date: date = Field(default_factory=date.today, index=True)
    metric: str = Field(index=True, max_length=20)
    minutes_optimal: int = Field(default=0, ge=0)
    goal_minutes: int = Field(default=120, ge=0)
    goal_reached_at: Optional[datetime.datetime] = Field(default=None)
    ip_address: Optional[str] = None

