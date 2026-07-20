"""
Data models for the application.
"""
from datetime import date
from enum import Enum
from typing import Optional, Any, List
import json

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON as jsonType

class analyticsTimeslot(SQLModel, table=True):
    """
    Csv analytic file with parsed data
    """
    __tablename__ = "analyticsTimeslot"
    __tableArgs__ = {"extendExisting": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    data: List[dict] = Field(default=[], sa_column=Column(jsonType))

class analyticsTimeslotRead(SQLModel):
    """
    Csv analytic file
    """
    id: Optional[int] = None
    data: List[dict] = []

class analyticsTimeslotCreate(SQLModel):
    """
    Csv analytic file
    """
    id: Optional[int] = None
    data: List[dict] = []

class analyticsTimeslotUpdate(SQLModel):
    """
    Csv analytic file
    """
    id: Optional[int] = None
    data: Optional[List[dict]] = None

class lesson(SQLModel, table=True):
    """
    The difference between the two csv files (créneau prévu and créneau placé)
    """
    __tableArgs__ = {"extendExisting": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    codeEns: str
    codeResSae: str
    week: str
    typeEns: str
    hour: float
    isValid: bool = Field(default=False)
    isLesson: bool = Field(default=True)

class lessonRead(SQLModel):
    """
    Read schema for lesson 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    codeEns: str
    codeResSae: str
    week: str
    typeEns: str
    hour: float
    isValid: bool = Field(default=False)
    isLesson: bool = Field(default=True)

class lessonCreate(SQLModel):
    """
    Create schema for lesson 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    codeEns: str
    codeResSae: str
    week: str
    typeEns: str
    hour: float
    isValid: bool = Field(default=False)
    isLesson: bool = Field(default=True)

class lessonUpdate(SQLModel):
    """
    Update schema for lesson 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    codeEns: str
    codeResSae: str
    week: str
    typeEns: str
    hour: float
    isValid: bool = Field(default=False)
    isLesson: bool = Field(default=True)