from pydantic import BaseModel, validator
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

    @validator("password")
    def password_valide(cls, v):
        if len(v) < 6:
            raise ValueError("Mot de passe trop court (minimum 6 caractères)")
        if len(v.encode('utf-8')) > 72:
            raise ValueError("Mot de passe trop long (maximum 72 caractères)")
        return v

    @validator("username")
    def username_valide(cls, v):
        if len(v) < 4:
            raise ValueError("Identifiant trop court (minimum 4 caractères)")
        return v

class User(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class PatientResume(BaseModel):
    id: int
    nom_complet: str
    email: str
    class Config:
        from_attributes = True
