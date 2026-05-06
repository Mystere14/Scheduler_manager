"""
Data models for the application.
"""
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


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


class Cours(SQLModel, table=True):
    """
    Session table
    """
    __tablename__ = "cours"
    id: Optional[int] = Field(default=None, primary_key=True)
    code_res_sae: str
    semaine: str
    type_ens: Type_ens
    code_ens: str = Field(foreign_key="Code_ens.code")
    volume: int
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
    volume: int
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
    volume: int
    jour: str
    heure: int


class CoursUpdate(SQLModel):
    """
    Cours update schema
    """
    code_res_sae: Optional[str] = None
    semaine: Optional[str] = None
    type_ens: Optional[Type_ens] = None
    volume: Optional[int] = None
    jour: Optional[str] = None
    heure: Optional[int] = None


class Absence(SQLModel, table=True):
    """
    Absence table
    """
    __tablename__ = "absence"
    id: Optional[int] = Field(default=None, primary_key=True)
    enseignant: str = Field(foreign_key="Code_ens.code")
    heure_debut: int
    heure_fin: int
    jour: str
    description: Optional[str] = None

class AbsenceRead(SQLModel):
    """
    Absence read schema
    """
    id: int
    enseignant: str
    heure_debut: int
    heure_fin: int
    jour: str
    description: Optional[str] = None 

class AbsenceCreate(SQLModel):
    """
    Absence creation schema
    """
    enseignant: str
    heure_debut: int
    heure_fin: int
    jour: str
    description: Optional[str] = None

class AbsenceUpdate(SQLModel):
    """
    Absence update schema
    """
    heure_debut: Optional[int] = None
    heure_fin: Optional[int] = None
    jour: Optional[str] = None
    description: Optional[str] = None
