import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/predict"

st.set_page_config(page_title="Prédiction Maladie Cardiaque", layout="centered")
st.title("Prédiction de Maladie Cardiaque")

st.sidebar.header("Paramètres du patient")
def user_input_features():
    age      = st.sidebar.slider("Âge", 29, 77, 54)
    sex      = st.sidebar.selectbox("Sexe (1 homme, 0 femme)", [1, 0])
    cp       = st.sidebar.selectbox("Type douleur thoracique (0–3)", [0,1,2,3])
    trestbps = st.sidebar.slider("Tension au repos (mmHg)", 94, 200, 131)
    chol     = st.sidebar.slider("Cholestérol (mg/dl)", 126, 564, 246)
    fbs      = st.sidebar.selectbox("Glycémie à jeun >120 mg/dl (1 oui, 0 non)", [1,0])
    restecg  = st.sidebar.selectbox("ECG repos (0–2)", [0,1,2])
    thalach  = st.sidebar.slider("Fréquence max (bpm)", 71, 202, 150)
    exang    = st.sidebar.selectbox("Angine d'effort (1 oui, 0 non)", [1,0])
    oldpeak  = st.sidebar.slider("Oldpeak", 0.0, 6.2, 1.0, 0.1)
    slope    = st.sidebar.selectbox("Pente ST (0–2)", [0,1,2])
    ca       = st.sidebar.selectbox("Nombre vaisseaux (0–3)", [0,1,2,3])
    thal     = st.sidebar.selectbox("Thalassémie (1–3)", [1,2,3])
    return {
        "age": age, "sex": sex, "cp": cp,
        "trestbps": trestbps, "chol": chol,
        "fbs": fbs, "restecg": restecg,
        "thalach": thalach, "exang": exang,
        "oldpeak": oldpeak, "slope": slope,
        "ca": ca, "thal": thal
    }

input_data = user_input_features()
df_input = pd.DataFrame([input_data])

if st.button("Prédire"):
    with st.spinner("En cours de prédiction..."):
        res = requests.post(API_URL, json=input_data)
        if res.status_code == 200:
            result = res.json()
            st.success(f"Prédiction : {'Maladie' if result['prediction']==1 else 'Pas de maladie'}")
            st.write(f"Probabilité : {result['probability']*100:.1f}%")
        else:
            st.error("Erreur lors de l'appel à l'API")

st.markdown("---")
st.subheader("Entrée fournie")
st.write(df_input)
