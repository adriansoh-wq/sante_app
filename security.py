from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import database, models # Assurez-vous que ces fichiers sont dans le même dossier

# Configuration (doit être identique à celle utilisée pour créer le token)
SECRET_KEY = "VOTRE_CLE_SECRETE_TRES_SECURISEE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
    """Hache le mot de passe en utilisant bcrypt."""
    return pwd_context.hash(password)

def verifier_password(plain_password, hashed_password):
    """Vérifie si le mot de passe en clair correspond au hachage."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Génère un token JWT pour l'utilisateur connecté."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Vérifie le token JWT et retourne l'utilisateur actuel.
    Si le token est invalide ou expiré, une erreur 401 est renvoyée.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
       
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
