"""
Data models for the application.
"""
from datetime import date
from enum import Enum
from typing import Optional, Any, List
import json

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON as JSON_Type

class analytics_timeslot(SQLModel, table=True):
    """
    Csv analytic file with parsed data
    """
    __tablename__ = "analytics_timeslot"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    data: List[dict] = Field(default=[], sa_column=Column(JSON_Type))

class analytics_timeslotRead(SQLModel):
    """
    Csv analytic file
    """
    id: Optional[int] = None
    data: List[dict] = []

class analytics_timeslotCreate(SQLModel):
    """
    Csv analytic file
    """
    id: Optional[int] = None
    data: List[dict] = []

class analytics_timeslotUpdate(SQLModel):
    """
    Csv analytic file
    """
    id: Optional[int] = None
    data: Optional[List[dict]] = None

class compare_scheduler(SQLModel, table=True):
    """
    The difference between the two csv files (créneau prévu and créneau placé)
    """
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    code_ens: str
    code_res_sae: str
    semaine: str
    type_ens: str
    heures: float
    real_session: bool = Field(default=False)

class compare_schedulerRead(SQLModel):
    """
    Read schema for compare_scheduler 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    code_ens: str
    code_res_sae: str
    semaine: str
    type_ens: str
    heures: float
    real_session: bool = Field(default=False)

class compare_schedulerCreate(SQLModel):
    """
    Create schema for compare_scheduler 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    code_ens: str
    code_res_sae: str
    semaine: str
    type_ens: str
    heures: float
    real_session: bool = Field(default=False)

class compare_schedulerUpdate(SQLModel):
    """
    Update schema for compare_scheduler 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    code_ens: str
    code_res_sae: str
    semaine: str
    type_ens: str
    heures: float
    real_session: bool = Field(default=False)
