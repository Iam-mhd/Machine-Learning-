# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import joblib, pandas as pd
from backend.auth import (
    authenticate_user, create_access_token,
    get_current_user, oauth2_scheme
)
from pydantic import BaseModel

app = FastAPI(title="Heart Disease Predictor")

# Schéma des données d’entrée
class PatientFeatures(BaseModel):
    age: float; sex: int; cp: int; trestbps: float; chol: float
    fbs: int; restecg: int; thalach: float; exang: int
    oldpeak: float; slope: int; ca: int; thal: int

# Charger votre pipeline (assurez-vous que le chemin est correct)
pipeline = joblib.load("backend/models/heart_pipeline_lr.pkl")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # On passe le username en sub
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict")
async def predict(
    features: PatientFeatures,
    current_user: dict = Depends(get_current_user)
):
    df = pd.DataFrame([features.dict()])
    proba = pipeline.predict_proba(df)[0,1]
    pred  = int(pipeline.predict(df)[0])
    return {"prediction": pred, "probability": proba}
