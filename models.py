from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base  # On importe la Base créée dans database.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="medecin") # "admin", "medecin" ou "patient"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    nom_complet = Column(String) # Sera stocké chiffré
    age = Column(Integer)
    genre = Column(String)
    poids = Column(Float)
    email = Column(String, unique=True, index=True) # Sera stocké chiffré
    groupe_sanguin = Column(String)
   
    # Relation : Un patient peut avoir plusieurs mesures
    # "back_populates" permet de retrouver facilement le patient depuis une mesure
    mesures = relationship("Mesure", back_populates="proprietaire", cascade="all, delete-orphan")

class Mesure(Base):
    __tablename__ = "mesures"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    rythme_cardiaque = Column(Integer)
    date_prise = Column(DateTime(timezone=True), server_default=func.now())
   
    # Clé étrangère pour lier la mesure à un patient précis
    patient_id = Column(Integer, ForeignKey("patients.id"))
   
    # Relation inverse
    proprietaire = relationship("Patient", back_populates="mesures")
