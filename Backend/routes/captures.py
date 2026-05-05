"""
Routes for managing Captures.
"""
# Standard library imports
from typing import List, Optional
import datetime

# Third-party imports
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

# Local imports
from database import engine, get_session
from models import (
    AcquisitionSystem,
    Capture,
    CaptureCreate,
    CaptureRead,
    State,
    SensorStatus,
    CaptureIoT,
)

from utils import save_to_db, is_sensor_data_anomalous, get_or_404
from mock_generator import generate_mock_history
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/captures",
    tags=["Captures"],
)


@router.post("/iot", response_model=CaptureRead)
# la gestion de l'ouverture/fermeture est centralisée dans get_session.
def create_capture_iot(iot_data: CaptureIoT, session: Session = Depends(get_session)): # systeme d injection de dépendance de FastAPI, récupère une session de base de données, la session est directement injecee dans les arg 
    """
    Create a new Capture from an IoT device (identified by IP).
    """
    # Find AcquisitionSystem by IP
    statement = select(AcquisitionSystem).where(AcquisitionSystem.addressIP == iot_data.ip)
    found_acquisition_system = session.exec(statement).first()
    
    if not found_acquisition_system:
        raise HTTPException(status_code=404, detail=f"AcquisitionSystem with IP '{iot_data.ip}' not found")
        

            
    # Update AcquisitionSystem latest values
    found_acquisition_system.temperature = iot_data.temperature
    found_acquisition_system.humidity = iot_data.humidity
    found_acquisition_system.co2 = iot_data.co2
    found_acquisition_system.tvoc = iot_data.tvoc
    
    # Update timestamp if this is a forced send
    if iot_data.forced_send:
        found_acquisition_system.last_forced_update = datetime.datetime.now()
    
    # Update sensor statuses if provided
    if iot_data.sensor_status:
        found_acquisition_system.dht22_status = iot_data.sensor_status.dht22
        found_acquisition_system.sgp30_status = iot_data.sensor_status.sgp30
        found_acquisition_system.oled_status = iot_data.sensor_status.oled
        
        # Detect anomaly based on sensor status
        if is_sensor_data_anomalous(iot_data.sensor_status, iot_data.temperature, iot_data.humidity, iot_data.co2, iot_data.tvoc):
            found_acquisition_system.ASState = State.Anomaly
        else:
            found_acquisition_system.ASState = State.Connected
    
    session.add(found_acquisition_system)


    # Check if AcquisitionSystem is linked to a room
    if not found_acquisition_system.room_name:
            raise HTTPException(status_code=404, detail=f"No Room configured for AcquisitionSystem '{found_acquisition_system.name}'")
            
        # Create Capture
    new_capture = Capture(
            temperature=iot_data.temperature,
            humidity=iot_data.humidity,
            co2=iot_data.co2,
            tvoc=iot_data.tvoc,
            roomName=found_acquisition_system.room_name,
            acquisition_system_name=found_acquisition_system.name
        )
        
    try:
            save_to_db(session, new_capture)
            return new_capture
    except Exception as exc:  # pragma: no cover - bubble up as HTTP error
            session.rollback()
            logger.exception("Failed to create capture from IoT data for IP %s", iot_data.ip)
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(exc)}") from exc


@router.get("/", response_model=List[CaptureRead])
def capture_list(session: Session = Depends(get_session)):
    """
    Get all Captures. If database is empty, returns mock data for 'Pixel' room.
    """
    captures = session.exec(select(Capture)).all()
    
    if len(captures) > 5:
        return captures
        
    # Validation fallback: generate mock data if DB is empty
    # Default to 'Pixel' room characteristics or generic values
    # Generate 365 days of data to support 'year' and 'max' views in frontend
    mock_data = generate_mock_history(21.0, 420.0, days=365)
    
    enriched_mock_data = []
    fake_id_counter = -1
    for pt in mock_data:
        # Create a dict that matches CaptureRead structure
        pt_copy = pt.copy()
        pt_copy["id"] = fake_id_counter
        pt_copy["roomName"] = "Pixel" 
        pt_copy["acquisition_system_name"] = "Simulated"
        enriched_mock_data.append(pt_copy)
        fake_id_counter -= 1
        
    return enriched_mock_data


@router.get("/{capture_id}", response_model=CaptureRead)
def get_capture(capture_id: int, session: Session = Depends(get_session)):
    """
    Get a Capture by ID.
    """
    existing_capture = get_or_404(session, Capture, capture_id, "Capture not found")
    return existing_capture


@router.delete("/{capture_id}")
def delete_capture(capture_id: int, session: Session = Depends(get_session)):
    """
    Delete a Capture by ID.
    """
    existing_capture = get_or_404(session, Capture, capture_id, "Capture not found")
    session.delete(existing_capture)
    session.commit()
    return {"detail": "Capture deleted successfully"}


@router.delete("/")
def delete_all_captures(session: Session = Depends(get_session)):
    """
    Delete all Captures.
    """
    captures = session.exec(select(Capture)).all()
    for capture in captures:
        session.delete(capture)
    session.commit()
    return {"detail": "All captures deleted successfully"}


@router.get("/room/{room_name}", response_model=List[CaptureRead])
def get_captures_by_room(
    room_name: str, 
    period: str = "day", 
    session: Session = Depends(get_session)
):
    """
    Get Captures by room name. 
    If not enough real data exists, generates mock data for demonstration.
    """
    # 1. Calcul de la durée demandée
    days_map = {"day": 1, "3days": 3, "week": 7, "month": 30, "max": 365}
    days = days_map.get(period, 1)

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)

    captures = session.exec(
        select(Capture)
        .where(Capture.roomName == room_name)
        .where(Capture.dateCapture >= cutoff_date)
        .order_by(Capture.dateCapture.desc())
    ).all()
    
    # Si on a suffisamment de données réelles, on les utilise
    if len(captures) > 5:
        return captures

    # SINON : Génération de données simulées
    # On cherche un SA lié pour avoir une température de base
    sa = session.exec(select(AcquisitionSystem).where(AcquisitionSystem.room_name == room_name)).first()
    
    base_temp = sa.temperature if sa and sa.temperature else 20.0
    base_co2 = sa.co2 if sa and sa.co2 else 400.0
    base_humidity = sa.humidity if sa and sa.humidity else 45.0
    base_tvoc = sa.tvoc if sa and sa.tvoc else 10.0

    mock_data = generate_mock_history(base_temp, base_co2, base_humidity, base_tvoc, days)
    
    # Adapter le format pour CaptureRead
    enriched_mock_data = []
    fake_id_counter = -1
    for pt in mock_data:
        pt["id"] = fake_id_counter
        pt["roomName"] = room_name
        pt["acquisition_system_name"] = sa.name if sa else "Simulated"
        enriched_mock_data.append(pt)
        fake_id_counter -= 1
        
    return enriched_mock_data
