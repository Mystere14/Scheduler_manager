"""
Data models for the application.
"""
from datetime import date
from enum import Enum
from typing import Optional, Any, List
import json

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON as JSON_Type


class Type_ens(str, Enum):
    """
    Enum for session types.
    """
    C="C"
    TD="TD"
    TP="TP"
    Aut="Aut."
    DS="DS"

class Code_ens(SQLModel, table=True):
    """
    Teacher table
    """
    __tablename__ = "Code_ens"
    __table_args__ = {"extend_existing": True}
    code: str = Field(primary_key=True, min_length=1, max_length=5)


class Code_ensRead(SQLModel):
    """
    Code_ens read schema
    """
    code: str


class Code_ensCreate(SQLModel):
    """
    Code_ens creation schema
    """
    code: str = Field(min_length=1, max_length=5)


class Code_ensUpdate(SQLModel):
    """
    Code_ens update schema
    """
    code: Optional[str] = Field(None, min_length=1, max_length=5)

class Input_cours(SQLModel, table=True):
    """
    input data table sent from csv
    """
    __tablename__ = "input_cours"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    code_res_sae: str
    semaine: str
    type_ens: str
    code_ens: str 
    volume: float

class Input_coursRead(SQLModel):
    """
    input_cours data read schema
    """
    code_res_sae: str
    semaine: str
    type_ens: str
    code_ens: str
    volume: float

class Input_coursCreate(SQLModel):
    """
    input_cours data creation schema
    """
    code_res_sae: str
    semaine: str
    type_ens: str
    code_ens: str
    volume: float

class Input_coursUpdate(SQLModel):
    """
    input_cours update schema
    """
    code_res_sae: Optional[str] = None
    semaine: Optional[str] = None
    type_ens: Optional[str] = None
    code_ens: Optional[str] = None
    volume: Optional[float] = None


class Cours(SQLModel, table=True):
    """
    Session table
    """
    __tablename__ = "cours"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    code_res_sae: str
    semaine: str
    type_ens: Type_ens
    code_ens: str = Field(foreign_key="Code_ens.code")
    volume: float
    jour: str
    heure: int


class CoursCreate(SQLModel):
    """
    Cours creation schema
    """
    code_res_sae: str
    semaine: str
    type_ens: Type_ens
    code_ens: str
    volume: float
    jour: str
    heure: int


class CoursRead(SQLModel):
    """
    Cours read schema
    """
    id: int
    code_res_sae: str
    semaine: str
    type_ens: Type_ens
    code_ens: str
    volume: float
    jour: str
    heure: int


class CoursUpdate(SQLModel):
    """
    Cours update schema
    """
    code_res_sae: Optional[str] = None
    semaine: Optional[str] = None
    type_ens: Optional[Type_ens] = None
    volume: Optional[float] = None
    jour: Optional[str] = None
    heure: Optional[int] = None


class Absence(SQLModel, table=True):
    """
    Absence table
    """
    __tablename__ = "absence"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    enseignant: str = Field(foreign_key="Code_ens.code")
    heure_debut: float
    heure_fin: float
    jour: date 
    description: Optional[str] = None

class AbsenceRead(SQLModel):
    """
    Absence read schema
    """
    id: int
    enseignant: str
    heure_debut: float
    heure_fin: float
    jour: date
    description: Optional[str] = None 

class AbsenceCreate(SQLModel):
    """
    Absence creation schema
    """
    enseignant: str
    heure_debut: float
    heure_fin: float
    jour: date = Field(default_factory=date.today)
    description: Optional[str] = None

class AbsenceUpdate(SQLModel):
    """
    Absence update schema
    """
    heure_debut: Optional[float] = None
    heure_fin: Optional[float] = None
    jour: Optional[date] = None
    description: Optional[str] = None


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
    type_ens: str
    heures: float
    real_session: bool = Field(default=False)
