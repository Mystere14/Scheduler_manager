import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import Session, select

from database import engine
from models import Absence, Analytics_creneau, Analytics_creneauCreate, Analytics_creneauRead, Analytics_creneauUpdate
from utils import save_to_db
from processed_data.creatCSVFromData import extract_calendar_data, parse_calendar_file 
from processed_data.compareCSVs import compare_schedulers_from_spreadsheets

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics_creneau",
    tags=["analytics_creneau"],
)

@router.get("/", response_model=List[dict])
def get_analytics_creneau_by_teacher():
    """
    Get the analytics_creneau data parsed from calendar.
    """
    delete_analytics_creneau()
    create_analytics_creneau()
    with Session(engine) as session:
        analytics_creneau_records = session.exec(
            select(Analytics_creneau)
        ).all()
        if not analytics_creneau_records:
            raise HTTPException(status_code=404, detail="No analytics_creneau found")
        
        # Extract and combine all data from all records
        all_data = []
        for record in analytics_creneau_records:
            if record.data:
                all_data.extend(record.data)
        
        return all_data if all_data else []
    
@router.post("/", response_model=Analytics_creneauCreate)
def create_analytics_creneau():
    """
    Create a new analytics_creneau.
    """
    parsed_data = extract_calendar_data()
    if parsed_data == -1:
        raise HTTPException(status_code=500, detail="Error fetching calendar data")
    
    new_analytics_creneau_data = Analytics_creneauCreate(data=parsed_data)
    new_analytics_creneau = Analytics_creneau(data=parsed_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_analytics_creneau)
            return new_analytics_creneau_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating analytics_creneau")
            raise HTTPException(
                status_code=409, detail="Error creating analytics_creneau"
            ) from exc
    
@router.post("/", response_model=Analytics_creneauCreate)
def create_analytics_creneau():
    """
    Create a new analytics_creneau.
    """
    parsed_data = extract_calendar_data()
    if parsed_data == -1:
        raise HTTPException(status_code=500, detail="Error fetching calendar data")
    
    new_analytics_creneau_data = Analytics_creneauCreate(data=parsed_data)
    new_analytics_creneau = Analytics_creneau(data=parsed_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_analytics_creneau)
            return new_analytics_creneau_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating analytics_creneau")
            raise HTTPException(
                status_code=409, detail="Error creating analytics_creneau"
            ) from exc
        
@router.post("/vcalendar", response_model=Analytics_creneauCreate)
async def create_analytics_creneau_from_vcalendar(file: UploadFile = File(...)):
    """
    Create a new analytics_creneau from uploaded vCalendar file.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Parse the calendar file
        parsed_data = parse_calendar_file(content)
        if parsed_data == -1:
            logger.error("parse_calendar_file returned -1, check logs above for details")
            raise HTTPException(status_code=400, detail="Error parsing calendar file")
        if not parsed_data:
            logger.error("parse_calendar_file returned empty data")
            raise HTTPException(status_code=400, detail="Calendar file contains no valid data")
        
        new_analytics_creneau_data = Analytics_creneauCreate(data=parsed_data)
        new_analytics_creneau = Analytics_creneau(data=parsed_data)

        with Session(engine) as session:
            try:
                save_to_db(session, new_analytics_creneau)
                return new_analytics_creneau_data
            except IntegrityError as exc:
                session.rollback()
                logger.exception("Integrity error creating analytics_creneau from vcalendar")
                raise HTTPException(
                    status_code=409, detail="Error creating analytics_creneau"
                ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing vcalendar file")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(exc)}")

@router.post("/withEachSpreadsheet", response_model=dict)
async def create_analytics_creneau_from_each_spreadsheet(FileschedulerPlanned: UploadFile = File(...),schedulerPlaced: UploadFile = File(...)):
    """
    Create a new analytics_creneau from csv files in purpose of creating a compare_scheduler.
    """
    try:
        # Read the file content
        contentSchedulerPlanned = await FileschedulerPlanned.read()
        contentSchedulerPlaced = await schedulerPlaced.read()
            
        compare_schedulers_from_spreadsheets(contentSchedulerPlanned, contentSchedulerPlaced)
        
        return {"message": "Comparison completed successfully"}
        
    except Exception as exc:
        logger.exception("Error comparing schedulers")
        raise HTTPException(status_code=500, detail=f"Error: {str(exc)}")



@router.put("/{analytics_creneau_id}", response_model=Analytics_creneauUpdate)
def update_analytics_creneau(analytics_creneau_id: int, analytics_creneau_data: Analytics_creneauUpdate):
    """
    Update an existing analytics_creneau.
    """
    with Session(engine) as session:
        analytics_creneau = session.get(Analytics_creneau, analytics_creneau_id)
        if not analytics_creneau:
            raise HTTPException(status_code=404, detail="Analytics_creneau not found")
        
        # Update only provided fields
        update_data = analytics_creneau_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(analytics_creneau, key, value)
        
        try:
            save_to_db(session, analytics_creneau)
            return analytics_creneau
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating analytics_creneau %s", analytics_creneau_id)
            raise HTTPException(
                status_code=409, detail=f"Error updating analytics_creneau with ID '{analytics_creneau_id}'"
            ) from exc

def delete_analytics_creneau():
    """
    Delete all analytics_creneau from database.
    """
    with Session(engine) as session:
        # Fetch and delete all records
        statement = select(Analytics_creneau)
        all_records = session.exec(statement).all()
        for record in all_records:
            session.delete(record)
        session.commit()

