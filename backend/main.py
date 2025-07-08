# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import pandas as pd, joblib

from backend.auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_bearer,
)

app = FastAPI(title="Heart Disease Predictor")

# input schema
class PatientFeatures(BaseModel):
    age: float
    sex: int
    cp: int
    trestbps: float
    chol: float
    fbs: int
    restecg: int
    thalach: float
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

# chargez votre pipeline entraîné
pipeline = joblib.load("backend/models/heart_pipeline_lr.pkl")

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/predict")
async def predict(
    features: PatientFeatures,
    current_user: dict = Depends(get_current_user_from_bearer),
):
    df = pd.DataFrame([features.dict()])
    proba = pipeline.predict_proba(df)[0, 1]
    pred  = int(pipeline.predict(df)[0])
    return {"prediction": pred, "probability": proba}