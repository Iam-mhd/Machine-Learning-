from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import joblib, pandas as pd

from auth import authenticate_user, create_access_token, get_current_user, oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(title="Heart Disease Predictor")

# Charger le pipeline
pipeline = joblib.load("backend/models/heart_pipeline_lr.pkl")

# Schéma d’entrée
class PatientFeatures(BaseModel):
    age: float; sex: int; cp: int; trestbps: float; chol: float
    fbs: int; restecg: int; thalach: float; exang: int
    oldpeak: float; slope: int; ca: int; thal: int

# Endpoint pour obtenir un token
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Identifiants incorrects")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# Endpoint protégé
@app.post("/predict")
def predict(
    data: PatientFeatures,
    current_user: dict = Depends(get_current_user)
):
    df = pd.DataFrame([data.dict()])
    proba = pipeline.predict_proba(df)[0,1]
    pred  = int(pipeline.predict(df)[0])
    return {"prediction": pred, "probability": round(proba,3)}
