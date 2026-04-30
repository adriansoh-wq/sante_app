from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func
import models, schemas, database, security

app = FastAPI()
ALLOW_REGISTRATION = True

# Création des tables au démarrage
models.Base.metadata.create_all(bind=database.engine)

@app.get("/ping")
def ping():
    return {"status": "alive"}

# ==========================================
# ROUTES PUBLIQUES (ACCÈS LIBRE)
# ==========================================

@app.post("/public/enregistrer_dossier/", response_model=schemas.Patient)
def creer_dossier_complet(patient: schemas.PatientCreate, db: Session = Depends(database.get_db)):
    """Permet à un patient de créer son profil et d'enregistrer ses données."""
    # On vérifie si l'email existe déjà
    db_patient = db.query(models.Patient).filter(models.Patient.email == patient.email).first()
    if db_patient:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    donnees_patient = patient.dict()
    temp = donnees_patient.pop("temperature")
    pouls = donnees_patient.pop("rythme_cardiaque")

    # Création du patient
    nouveau_patient = models.Patient(**donnees_patient)
    db.add(nouveau_patient)
    db.commit()
    db.refresh(nouveau_patient)

    if temp is not None and pouls is not None:
        nouvelle_mesure = models.Mesure(
            temperature=temp,
            rythme_cardiaque=pouls,
            patient_id=nouveau_patient.id # C'est ici que le lien se fait !
        )
        db.add(nouvelle_mesure)
        db.commit()

    return nouveau_patient

@app.get("/public/saisies_par_jour")
def saisies_par_jour(db: Session = Depends(database.get_db)):
   
    # Récupère les 7 derniers jours
    aujourd_hui = datetime.now().date()
    sept_jours = aujourd_hui - timedelta(days=6)
   
    # Compte les mesures groupées par jour
    resultats = db.query(
        func.date(models.Mesure.date_prise).label("jour"),
        func.count(models.Mesure.id).label("total")
    ).filter(
        models.Mesure.date_prise >= sept_jours
    ).group_by(
        func.date(models.Mesure.date_prise)
    ).all()
   
    # Crée un dictionnaire avec tous les 7 jours (même si = 0)
    jours_map = {}
    for i in range(7):
        jour = sept_jours + timedelta(days=i)
        jours_map[str(jour)] = 0
   
    # Remplie avec les vraies données
    for r in resultats:
        jours_map[str(r.jour)] = r.total
   
    # Formate pour le frontend
    noms_jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    response = []
    for date_str, total in jours_map.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        response.append({
            "Jour": noms_jours[date_obj.weekday()],
            "Date": date_str,
            "Saisies": total
        })
   
    return response

@app.get("/public/stats_globales")
def obtenir_stats_publiques(db: Session = Depends(database.get_db)):
    # Récupérer toutes les mesures de la base de données
    mesures = db.query(models.Mesure).all()
   
    if not mesures:
        return {
            "temp_moyenne": 0,
            "pouls_moyen": 0,
            "total_relevés": 0,
            "historique_temp": [] # Liste vide si pas de données
        }
   
    # Calcul des moyennes
    moy_temp = sum(m.temperature for m in mesures) / len(mesures)
    moy_pouls = sum(m.rythme_cardiaque for m in mesures) / len(mesures)
    # EXTRACTION DE LA LISTE DES TEMPÉRATURES POUR LE GRAPHIQUE
    # On récupère les 20 dernières températures pour ne pas surcharger le graph
    historique = [m.temperature for m in mesures][-20:]
   
    return {
        "temp_moyenne": round(moy_temp, 1),
        "pouls_moyen": int(moy_pouls),
        "total_relevés": len(mesures),
        "historique_temp": historique # On envoie les vraies données ici
    }

@app.get("/public/toutes_mesures")
def toutes_mesures(db: Session = Depends(database.get_db)):
    mesures = db.query(models.Mesure).all()
    if not mesures:
        return []
    return [
        {
            "temperature": m.temperature,
            "rythme_cardiaque": m.rythme_cardiaque
        }
        for m in mesures
    ]
# ==========================================
# ROUTES PROTÉGÉES (MÉDECIN UNIQUEMENT)
# ==========================================

@app.post("/register", response_model=schemas.User)
def créer_compte_medecin(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Vérifier si l'utilisateur existe déjà
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")
   
    # 2. Hacher le mot de passe avant de l'enregistrer
    # (Utilisez bien le nom de fonction présent dans votre security.py)
    hashed_pw = security.hash_password(user.password)
   
    # 3. Créer l'entrée dans la base de données
    nouveau_medecin = models.User(
        username=user.username,
        hashed_password=hashed_pw
    )
   
    db.add(nouveau_medecin)
    db.commit()
    db.refresh(nouveau_medecin)
   
    return nouveau_medecin

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # On cherche l'utilisateur dans la base de données
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verifier_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Identifiants incorrects")
   
    access_token = security.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/medecin/patient/{patient_id}", response_model=schemas.Patient)
def consulter_dossier_prive(
    patient_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user) # VERROU DE SÉCURITÉ
):
    """Seul un médecin authentifié peut voir le détail nom/prénom et les graphiques."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return patient
    
@app.post("/register/medecin")
def register_medecin(medecin: dict, db: Session = Depends(get_db)):
    if not ALLOW_REGISTRATION:
        raise HTTPException(status_code=403, detail="L'inscription est actuellement désactivée.")
   
    # Vérifier si l'email existe déjà
    db_user = db.query(models.Medecin).filter(models.Medecin.email == medecin['email']).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
   
    # Hachage du mot de passe avant enregistrement
    hashed_password = security.pwd_context.hash(medecin['password'])
   
    noueau_medecin = models.Medecin(
        nom=medecin['nom'],
        specialite=medecin['specialite'],
        email=medecin['email'],
        hashed_password=hashed_password
    )
   
    db.add(noueau_medecin)
    db.commit()
    return {"message": "Compte médecin créé avec succès !"}

