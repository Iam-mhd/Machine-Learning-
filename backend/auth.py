# backend/auth.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from dotenv import load_dotenv
import os

# --- Chargement des secrets ---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# on définit explicitement le flow "password" pour Swagger
oauth2_scheme = OAuth2(
    flows=OAuthFlowsModel(
        password={"tokenUrl": "/token", "scopes": {}}
    )
)

# DB factice
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("monpassword")
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return {"username": username}

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Génère un JWT contenant :
      - claim 'exp' (expiration)
      - claim 'sub' (subject) = nom de l'utilisateur
    """
    # S’assurer que SECRET_KEY est bien défini
    if SECRET_KEY is None:
        raise RuntimeError("SECRET_KEY non configurée")
    to_encode = data.copy()
    # Récupère le nom d'utilisateur
    username = data.get("sub") or data.get("username")
    if username is None:
        raise RuntimeError("create_access_token: 'sub' manquant dans data")
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "sub": username})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return {"username": username}
