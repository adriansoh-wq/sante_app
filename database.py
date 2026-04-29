from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. EMPLACEMENT DE LA BASE DE DONNÉES
# Le fichier "sante_app.db" sera créé automatiquement dans votre dossier de projet.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sante_app.db")

# 2. CRÉATION DE L'ENGINE (Moteur de recherche)
# "check_same_thread=False" est nécessaire uniquement pour SQLite avec FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. CRÉATION DE LA SESSION
# C'est ce qui permet d'ouvrir une "conversation" avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. BASE POUR LES MODÈLES
# Tous vos modèles (Patient, User, Mesure) hériteront de cette classe
Base = declarative_base()

# 5. DÉPENDANCE POUR L'API
# Cette fonction permet à FastAPI de créer une session propre pour chaque requête
# et de la fermer automatiquement une fois terminé.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()