"""
Routes for managing Acquisition System (AcquisitionSystem).
"""
# pylint: disable=invalid-name
from typing import List
import httpx
from config import settings
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from database import engine
from models import AcquisitionSystem, AcquisitionSystemCreate, AcquisitionSystemRead, AcquisitionSystemUpdate, State, Room, Capture, Status
from utils import save_to_db, is_sensor_data_anomalous, get_or_404
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/acquisition_systems",
    tags=["Systèmes d'Acquisition (AcquisitionSystem)"],
)

@router.post("/", response_model=AcquisitionSystemRead)
async def create_acquisition_system(acquisition_system_data: AcquisitionSystemCreate):
    """
    Create a new Acquisition System.
    """
    new_acquisition_system = AcquisitionSystem.model_validate(acquisition_system_data)
    
    # Check if SA exists on the network if IP is provided
    if new_acquisition_system.addressIP:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{new_acquisition_system.addressIP}/ping",
                    timeout=settings.HTTP_PING_TIMEOUT_SECONDS,
                )
                if response.status_code == 200:
                    new_acquisition_system.ASState = State.Connected
                    new_acquisition_system.sensor = True
        except httpx.RequestError as exc:
            # Could not connect, but we still create the AcquisitionSystem. Log for debugging.
            logger.warning("Could not reach AcquisitionSystem at %s: %s", new_acquisition_system.addressIP, exc)

    with Session(engine) as session:
        try:
            save_to_db(session, new_acquisition_system)
            return new_acquisition_system
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating AcquisitionSystem %s", acquisition_system_data.name)
            raise HTTPException(
                status_code=409, detail=f"AcquisitionSystem with name '{acquisition_system_data.name}' already exists"
            ) from exc

@router.get("/", response_model=List[AcquisitionSystemRead])
def acquisition_system_list():
    """
    Get all Acquisition Systems.
    """
    with Session(engine) as session:
        acquisition_system_items = session.exec(select(AcquisitionSystem)).all()
        return acquisition_system_items


@router.get("/{name}", response_model=AcquisitionSystemRead)
def get_acquisition_system(name: str):
    """
    Get an Acquisition System by name.
    """
    with Session(engine) as session:
        existing_acquisition_system = get_or_404(session, AcquisitionSystem, name, "AcquisitionSystem not found")
        return existing_acquisition_system

@router.put("/{name}", response_model=AcquisitionSystemRead)
def update_acquisition_system(name: str, acquisition_system_update: AcquisitionSystemUpdate):
    """
    Update an Acquisition System's name.
    """
    with Session(engine) as session:
        existing_acquisition_system = get_or_404(session, AcquisitionSystem, name, "AcquisitionSystem not found")
        acquisition_system_data = acquisition_system_update.model_dump(exclude_unset=True)

        # Update fields on the existing acquisition system
        for key, value in acquisition_system_data.items():
            setattr(existing_acquisition_system, key, value)

        save_to_db(session, existing_acquisition_system)
            
        return existing_acquisition_system


@router.delete("/{name}")
def delete_acquisition_system(name: str):
    """
    Delete an Acquisition System.
    """
    with Session(engine) as session:
        existing_acquisition_system = get_or_404(session, AcquisitionSystem, name, "AcquisitionSystem not found")
        
        # Check if AcquisitionSystem is in a room and if that room needs to be updated
        if existing_acquisition_system.room_name:
            room_name = existing_acquisition_system.room_name
            # Check if there are other AcquisitionSystems in this room
            other_acquisition_system = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name).where(AcquisitionSystem.name != name)).all()
            if not other_acquisition_system:
                # No other AcquisitionSystem in the room, revert room status to Register
                existing_room = session.get(Room, room_name)
                if existing_room:
                    existing_room.status = Status.Register
                    session.add(existing_room)

        # Unlink Captures
        captures = session.exec(select(Capture).where(Capture.acquisition_system_name == name)).all()
        for capture in captures:
            capture.acquisition_system_name = None
            session.add(capture)

        session.delete(existing_acquisition_system)
        session.commit()
        return {"detail": "AcquisitionSystem deleted successfully"}


@router.get("/{name}/refresh", response_model=AcquisitionSystemRead)
async def refresh_acquisition_system(name: str):
    """
    Refresh AcquisitionSystem data by calling the device.
    """
    try:
        with Session(engine) as session:
            existing_acquisition_system = get_or_404(session, AcquisitionSystem, name, "AcquisitionSystem not found")
            
            if not existing_acquisition_system.addressIP:
                return existing_acquisition_system
            
            clean_ip = existing_acquisition_system.addressIP.strip()
            if not clean_ip:
                return existing_acquisition_system
                
            # Refresh data if device has an IP and is either in Experimentation OR Installation (allow early testing)
            # Added Register status to allow validation during initial setup (Calibration Step 3)
            if existing_acquisition_system.status not in (Status.Experimentation, Status.Installation, Status.Register):
                return existing_acquisition_system
            
            try:
                async with httpx.AsyncClient() as client:
                    # Assuming the AcquisitionSystem has a /data endpoint returning JSON
                    response = await client.get(
                        f"http://{clean_ip}/data",
                        timeout=settings.HTTP_DATA_TIMEOUT_SECONDS,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        # Update AcquisitionSystem: collect readings once, assign,
                        # then unpack to local variables for later checks.
                        units = ("temperature", "humidity", "co2", "tvoc")
                        values = {u: data.get(u) for u in units}

                        for u, v in values.items():
                            setattr(existing_acquisition_system, u, v)

                        temp, hum, co2, tvoc = (values[u] for u in units) # extract for anomaly check
                        
                        # Update sensor statuses if provided
                        sensor_status = data.get("sensor_status")
                        if sensor_status:
                            existing_acquisition_system.dht22_status = sensor_status.get("dht22")
                            existing_acquisition_system.sgp30_status = sensor_status.get("sgp30")
                            existing_acquisition_system.oled_status = sensor_status.get("oled")

                        # Centralized anomaly detection
                        if is_sensor_data_anomalous(sensor_status, temp, hum, co2, tvoc):
                            existing_acquisition_system.ASState = State.Anomaly
                        else:
                            existing_acquisition_system.ASState = State.Connected
                            
                        save_to_db(session, existing_acquisition_system)
                        
                        if existing_acquisition_system.room_name and all(v is not None for v in values.values()):
                                                    
                            capture_data = {
                                'temperature': existing_acquisition_system.temperature,
                                'humidity': existing_acquisition_system.humidity,
                                'co2': existing_acquisition_system.co2,
                                'tvoc': existing_acquisition_system.tvoc,
                                'roomName': existing_acquisition_system.room_name,
                                'acquisition_system_name': existing_acquisition_system.name
                            }

                            try:
                                # Verify if room exists to avoid IntegrityError
                                if session.get(Room, existing_acquisition_system.room_name):
                                    new_capture = Capture(**capture_data)
                                    save_to_db(session, new_capture)
                            except Exception as e:
                                logger.error(f"Failed to create capture after refresh: {e}")
                        else:
                            logger.warning(f"Cannot create capture after refresh - room_name: {existing_acquisition_system.room_name}, values valid: {all(v is not None for v in values.values())}")
                            
                    else:
                        existing_acquisition_system.ASState = State.Anomaly
                        save_to_db(session, existing_acquisition_system)

            except httpx.HTTPError as exc:
                # Device not reachable — mark as offline and log socket error
                # Use getattr to safely check for Offline state, fallback to Anomaly or similar if model changed
                existing_acquisition_system.ASState = State.Offline if hasattr(State, 'Offline') else State.Anomaly
                
                # Attempt to save state, but catch potential DB errors to avoid crash
                try:
                    save_to_db(session, existing_acquisition_system)
                except Exception as db_exc:
                    logger.error(f"Failed to update AS state to Offline: {db_exc}")
                    
                logger.warning(
                    "Failed to refresh AcquisitionSystem %s at %s: %s",
                    name,
                    clean_ip,
                    exc,
                )
            except Exception as e:
                logger.error(f"Unexpected error inside refresh logic for {name}: {e}")
                
            return existing_acquisition_system
            
    except Exception as e:
        logger.error(f"Critical error in refresh_acquisition_system wrapper: {e}")
        # Re-raise HTTPException (like 404) so it's handled correctly by FastAPI
        if isinstance(e, HTTPException):
            raise e
        # For other unexpected errors, raise 500 but log it first
        raise HTTPException(status_code=500, detail=f"Internal Server Error during refresh: {str(e)}")


@router.get("/status/{status}", response_model=List[AcquisitionSystemRead])
def get_acquisition_system_list_by_status(status: str):
    """
    Get Acquisition Systems by status.
    """
    with Session(engine) as session:
        acquisition_system_items = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.status == status)).all()
        return acquisition_system_items
