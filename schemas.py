from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- SCHÉMAS POUR LES MESURES ---
class MesureBase(BaseModel):
    temperature: float
    rythme_cardiaque: int

class MesureCreate(MesureBase):
    pass

class Mesure(MesureBase):
    id: int
    date_prise: datetime
    class Config:
        from_attributes = True

# --- SCHÉMAS POUR LES PATIENTS ---
class PatientBase(BaseModel):
    nom_complet: str
    age: int
    genre: str
    poids: float
    groupe_sanguin: str
    email: str

class PatientCreate(PatientBase):
    temperature: Optional[float] = None
    rythme_cardiaque: Optional[int] = None

class Patient(PatientBase):
    id: int
    mesures: List[Mesure] = []
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True