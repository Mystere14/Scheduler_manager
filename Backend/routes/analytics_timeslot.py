import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import Session, select

from database import engine
from models import analytics_timeslot, analytics_timeslotCreate, analytics_timeslotRead, analytics_timeslotUpdate
from utils import save_to_db
from processed_data.creatCSVFromData import extract_calendar_data, parse_calendar_file 
from processed_data.compareCSVs import lesson_from_spreadsheets
from processed_data.preprocessedPlannedScheduler import preprocessSchedulerPlanned


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics_timeslot",
    tags=["analytics_timeslot"],
)

@router.get("/", response_model=List[dict])
def get_analytics_timeslot_by_teacher():
    """
    Get the analytics_timeslot data parsed from calendar.
    """
    delete_analytics_timeslot()
    create_analytics_timeslot()
    with Session(engine) as session:
        analytics_timeslot_records = session.exec(
            select(Analytics_timeslot)
        ).all()
        if not analytics_timeslot_records:
            raise HTTPException(status_code=404, detail="No analytics_timeslot found")
        
        # Extract and combine all data from all records
        all_data = []
        for record in analytics_timeslot_records:
            if record.data:
                all_data.extend(record.data)
        
        return all_data if all_data else []
    
@router.post("/", response_model=analytics_timeslotCreate)
def create_analytics_timeslot():
    """
    Create a new analytics_timeslot.
    """
    parsed_data = extract_calendar_data()
    if parsed_data == -1:
        raise HTTPException(status_code=500, detail="Error fetching calendar data")
    
    new_analytics_timeslot_data = analytics_timeslotCreate(data=parsed_data)
    new_analytics_timeslot = analytics_timeslot(data=parsed_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_analytics_timeslot)
            return new_analytics_timeslot_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating analytics_timeslot")
            raise HTTPException(
                status_code=409, detail="Error creating analytics_timeslot"
            ) from exc
    
@router.post("/", response_model=analytics_timeslotCreate)
def create_analytics_timeslot():
    """
    Create a new analytics_timeslot.
    """
    parsed_data = extract_calendar_data()
    if parsed_data == -1:
        raise HTTPException(status_code=500, detail="Error fetching calendar data")
    
    new_analytics_timeslot_data = analytics_timeslotCreate(data=parsed_data)
    new_analytics_timeslot = analytics_timeslot(data=parsed_data)

    with Session(engine) as session:
        try:
            save_to_db(session, new_analytics_timeslot)
            return new_analytics_timeslot_data
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating analytics_timeslot")
            raise HTTPException(
                status_code=409, detail="Error creating analytics_timeslot"
            ) from exc
        
@router.post("/vcalendar", response_model=analytics_timeslotCreate)
async def create_analytics_timeslot_from_vcalendar(file: UploadFile = File(...)):
    """
    Create a new analytics_timeslot from uploaded vCalendar file.
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
        
        new_analytics_timeslot_data = analytics_timeslotCreate(data=parsed_data)
        new_analytics_timeslot = analytics_timeslot(data=parsed_data)

        with Session(engine) as session:
            try:
                save_to_db(session, new_analytics_timeslot)
                return new_analytics_timeslot_data
            except IntegrityError as exc:
                session.rollback()
                logger.exception("Integrity error creating analytics_timeslot from vcalendar")
                raise HTTPException(
                    status_code=409, detail="Error creating analytics_timeslot"
                ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing vcalendar file")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(exc)}")


@router.post("/preprocessedSchedulerPlanned", response_model=analytics_timeslotCreate)
async def create_analytics_timeslot_by_preprocessed_scheduler_planned(file: UploadFile = File(...)):
    """
    Create a new analytics_timeslot from uploaded preprocessed scheduler planned file.
    """
    try:
        # Read the file content
        content = await file.read()
        
        preprocessed_data = preprocessSchedulerPlanned(content)
        if preprocessed_data == -1:
            logger.error("preprocessSchedulerPlanned returned -1, check logs above for details")
            raise HTTPException(status_code=400, detail="Error preprocessing scheduler planned file")
        if not preprocessed_data:
            logger.error("preprocessSchedulerPlanned returned empty data")
            raise HTTPException(status_code=400, detail="Scheduler planned file contains no valid data")
        
        new_analytics_timeslot_data = analytics_timeslotCreate(data=preprocessed_data)
        new_analytics_timeslot = analytics_timeslot(data=preprocessed_data)

        with Session(engine) as session:
            try:
                save_to_db(session, new_analytics_timeslot)
                print(f"data: {new_analytics_timeslot_data}")
                return new_analytics_timeslot_data
            except IntegrityError as exc:
                session.rollback()
                logger.exception("Integrity error creating analytics_timeslot from preprocessed scheduler planned")
                raise HTTPException(
                    status_code=409, detail="Error creating analytics_timeslot"
                ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing preprocessed scheduler planned file")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(exc)}")


@router.post("/withEachSpreadsheet", response_model=dict)
async def create_analytics_timeslot_from_each_spreadsheet(FileschedulerPlanned: UploadFile = File(...),schedulerPlaced: UploadFile = File(...)):
    """
    Create a new analytics_timeslot from csv files in purpose of creating a session.
    """
    try:
        # Read the file content
        contentSchedulerPlanned = await FileschedulerPlanned.read()
        contentSchedulerPlaced = await schedulerPlaced.read()
            
        lesson_from_spreadsheets(contentSchedulerPlanned, contentSchedulerPlaced)
        
        return {"message": "Comparison completed successfully"}
        
    except Exception as exc:
        logger.exception("Error comparing schedulers")
        raise HTTPException(status_code=500, detail=f"Error: {str(exc)}")



@router.put("/{analytics_timeslot_id}", response_model=analytics_timeslotUpdate)
def update_analytics_timeslot(analytics_timeslot_id: int, analytics_timeslot_data: analytics_timeslotUpdate):
    """
    Update an existing analytics_timeslot.
    """
    with Session(engine) as session:
        analytics_timeslot = session.get(analytics_timeslot, analytics_timeslot_id)
        if not analytics_timeslot:
            raise HTTPException(status_code=404, detail="analytics_timeslot not found")
        
        # Update only provided fields
        update_data = analytics_timeslot_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(analytics_timeslot, key, value)
        
        try:
            save_to_db(session, analytics_timeslot)
            return analytics_timeslot
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating analytics_timeslot %s", analytics_timeslot_id)
            raise HTTPException(
                status_code=409, detail=f"Error updating analytics_timeslot with ID '{analytics_timeslot_id}'"
            ) from exc

def delete_analytics_timeslot():
    """
    Delete all analytics_timeslot from database.
    """
    with Session(engine) as session:
        # Fetch and delete all records
        statement = select(analytics_timeslot)
        all_records = session.exec(statement).all()
        for record in all_records:
            session.delete(record)
        session.commit()

