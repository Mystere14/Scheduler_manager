import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
from sqlmodel import Session, select

from database import engine
from models import analyticsTimeslot, analyticsTimeslotCreate, analyticsTimeslotRead, analyticsTimeslotUpdate
from utils import saveToDb
from processedData.creatCSVFromData import parseCalendarFile 
from processedData.compareCSVs import lessonFromSpreadsheets
from processedData.preprocessedPlannedScheduler import preprocessSchedulerPlanned
from routes.lesson import deleteTrueLesson

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analyticsTimeslot",
    tags=["analyticsTimeslot"],
)

@router.get("/", response_model=List[dict])
def getAnalyticsTimeslotByTeacher():
    """
    Get the analyticsTimeslot data parsed from calendar.
    """
    deleteTrueLesson()
    createAnalyticsTimeslot()
    with Session(engine) as session:
        analyticsTimeslotRecords = session.exec(
            select(analyticsTimeslot)
        ).all()
        if not analyticsTimeslotRecords:
            raise HTTPException(statusCode=404, detail="No analyticsTimeslot found")
        
        # Extract and combine all data from all records
        allData = []
        for record in analyticsTimeslotRecords:
            if record.data:
                allData.extend(record.data)
        
        return allData if allData else []
    
@router.post("/", response_model=analyticsTimeslotCreate)
def createAnalyticsTimeslot():
    """
    Create a new analyticsTimeslot.
    """
    parsedData = extractCalendarData()
    if parsedData == -1:
        raise HTTPException(status_code=500, detail="Error fetching calendar data")
    
    newAnalyticsTimeslotData = analyticsTimeslotCreate(data=parsedData)
    newAnalyticsTimeslot = analyticsTimeslot(data=parsedData)

    with Session(engine) as session:
        try:
            saveToDb(session, newAnalyticsTimeslot)
            return newAnalyticsTimeslotData
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating analyticsTimeslot")
            raise HTTPException(
                status_code=409, detail="Error creating analyticsTimeslot"
            ) from exc
    
@router.post("/", response_model=analyticsTimeslotCreate)
def createAnalyticsTimeslot():
    """
    Create a new analyticsTimeslot.
    """
    parsedData = extractCalendarData()
    if parsedData == -1:
        raise HTTPException(status_code=500, detail="Error fetching calendar data")
    
    newAnalyticsTimeslotData = analyticsTimeslotCreate(data=parsedData)
    newAnalyticsTimeslot = analyticsTimeslot(data=parsedData)

    with Session(engine) as session:
        try:
            saveToDb(session, newAnalyticsTimeslot)
            return newAnalyticsTimeslotData
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error creating analyticsTimeslot")
            raise HTTPException(
                status_code=409, detail="Error creating analyticsTimeslot"
            ) from exc
        
@router.post("/vcalendar", response_model=analyticsTimeslotCreate)
async def createAnalyticsTimeslotFromVcalendar(file: UploadFile = File(...)):
    """
    Create a new analyticsTimeslot from uploaded vCalendar file.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Parse the calendar file
        parsedData = parseCalendarFile(content)
        if parsedData == -1:
            logger.error("parseCalendarFile returned -1, check logs above for details")
            raise HTTPException(status_code=400, detail="Error parsing calendar file")
        if not parsedData:
            logger.error("parseCalendarFile returned empty data")
            raise HTTPException(status_code=400, detail="Calendar file contains no valid data")
        
        newAnalyticsTimeslotData = analyticsTimeslotCreate(data=parsedData)
        newAnalyticsTimeslot = analyticsTimeslot(data=parsedData)

        with Session(engine) as session:
            try:
                saveToDb(session, newAnalyticsTimeslot)
                return newAnalyticsTimeslotData
            except IntegrityError as exc:
                session.rollback()
                logger.exception("Integrity error creating analyticsTimeslot from vcalendar")
                raise HTTPException(
                    status_code=409, detail="Error creating analyticsTimeslot"
                ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing vcalendar file")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(exc)}")


@router.post("/preprocessedSchedulerPlanned", response_model=analyticsTimeslotCreate)
async def createAnalyticsTimeslotByPreprocessedSchedulerPlanned(file: UploadFile = File(...)):
    """
    Create a new analyticsTimeslot from uploaded preprocessed scheduler planned file.
    """
    try:
        # Read the file content
        deleteTrueLesson()

        content = await file.read()
        
        preprocessedData = preprocessSchedulerPlanned(content)
        if preprocessedData == -1:
            logger.error("preprocessSchedulerPlanned returned -1, check logs above for details")
            raise HTTPException(status_code=400, detail="Error preprocessing scheduler planned file")
        if not preprocessedData:
            logger.error("preprocessSchedulerPlanned returned empty data")
            raise HTTPException(status_code=400, detail="Scheduler planned file contains no valid data")
        
        newAnalyticsTimeslotData = analyticsTimeslotCreate(data=preprocessedData)
        newAnalyticsTimeslot = analyticsTimeslot(data=preprocessedData)

        with Session(engine) as session:
            try:
                saveToDb(session, newAnalyticsTimeslot)
                return newAnalyticsTimeslotData
            except IntegrityError as exc:
                session.rollback()
                logger.exception("Integrity error creating analyticsTimeslot from preprocessed scheduler planned")
                raise HTTPException(
                    status_code=409, detail="Error creating analyticsTimeslot"
                ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing preprocessed scheduler planned file")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(exc)}")


@router.post("/withEachSpreadsheet", response_model=dict)
async def createAnalyticsTimeslotFromEachSpreadsheet(FileschedulerPlanned: UploadFile = File(...),schedulerPlaced: UploadFile = File(...)):
    """
    Create a new analyticsTimeslot from csv files in purpose of creating a session.
    """
    try:
        # Read the file content
        contentSchedulerPlanned = await FileschedulerPlanned.read()
        contentSchedulerPlaced = await schedulerPlaced.read()
            
        lessonFromSpreadsheets(contentSchedulerPlanned, contentSchedulerPlaced)

        return {"message": "Comparison completed successfully"}
        
    except Exception as exc:
        logger.exception("Error comparing schedulers")
        raise HTTPException(status_code=500, detail=f"Error: {str(exc)}")



@router.put("/{analyticsTimeslotId}", response_model=analyticsTimeslotUpdate)
def updateAnalyticsTimeslot(analyticsTimeslotId: int, analyticsTimeslotData: analyticsTimeslotUpdate):
    """
    Update an existing analyticsTimeslot.
    """
    with Session(engine) as session:
        analyticsTimeslot = session.get(analyticsTimeslot, analyticsTimeslotId)
        if not analyticsTimeslot:
            raise HTTPException(status_code=404, detail="analyticsTimeslot not found")
        
        # Update only provided fields
        updateData = analyticsTimeslotData.model_dump(exclude_unset=True)
        for key, value in updateData.items():
            setattr(analyticsTimeslot, key, value)
        
        try:
            saveToDb(session, analyticsTimeslot)
            return analyticsTimeslot
        except IntegrityError as exc:
            session.rollback()
            logger.exception("Integrity error updating analyticsTimeslot %s", analyticsTimeslotId)
            raise HTTPException(
                status_code=409, detail=f"Error updating analyticsTimeslot with ID '{analyticsTimeslotId}'"
            ) from exc

def deleteAnalyticsTimeslot():
    """
    Delete all analyticsTimeslot from database.
    """
    with Session(engine) as session:
        # Fetch and delete all records
        statement = select(analyticsTimeslot)
        allRecords = session.exec(statement).all()
        for record in allRecords:
            session.delete(record)
        session.commit()

