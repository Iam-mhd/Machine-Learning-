# frontend/app_streamlit.py

import os
import streamlit as st
import requests

# 1) En local, Streamlit lit frontend/.streamlit/secrets.toml
#    [general]
#    API_URL = "https://maladie-cardiaque.onrender.com"
#
# 2) En prod, Render expose API_URL via une Env Var
API_URL = st.secrets.get("general", {}).get("API_URL") or os.getenv("API_URL")

if API_URL is None:
    st.error("Veuillez définir l'URL de l'API dans .streamlit/secrets.toml ou via la var d'env API_URL")
    st.stop()

st.title("Prédiction de maladie cardiaque")
st.write("Entrez les paramètres du patient pour obtenir une prédiction")

with st.form("patient_form"):
    age      = st.number_input("Âge", min_value=1, max_value=120, value=63, step=1)
    sex      = st.selectbox("Sexe (0=Femme, 1=Homme)", [0, 1])
    cp       = st.selectbox("Type douleur thoracique (0–3)", [0,1,2,3])
    trestbps = st.number_input("Tension artérielle (mmHg)", value=145, step=1)
    chol     = st.number_input("Cholestérol (mg/dl)", value=233, step=1)
    fbs      = st.selectbox("Glycémie à jeun>120 mg/dl (0/1)", [0,1])
    restecg  = st.selectbox("ECG au repos (0–2)", [0,1,2])
    thalach  = st.number_input("Fréq. cardiaque max", value=150, step=1)
    exang    = st.selectbox("Angine induite par effort (0/1)", [0,1])
    oldpeak  = st.number_input("Ancien pic (oldpeak)", value=2.3, format="%.1f")
    slope    = st.selectbox("Slope (0–2)", [0,1,2])
    ca       = st.selectbox("Nombre de vaisseaux colorés (0–4)", [0,1,2,3,4])
    thal     = st.selectbox("Thal (0=normal,1=fixed,2=reversible)", [0,1,2])
    submitted = st.form_submit_button("Prédire")

if submitted:
    payload = {
        "age": age, "sex": sex, "cp": cp, "trestbps": trestbps,
        "chol": chol, "fbs": fbs, "restecg": restecg,
        "thalach": thalach, "exang": exang, "oldpeak": oldpeak,
        "slope": slope, "ca": ca, "thal": thal
    }
    try:
        res = requests.post(f"{API_URL}/predict", json=payload)
        res.raise_for_status()
        data = res.json()
        st.success(f"Prediction : **{data['prediction']}**, probabilité : {data['probability']:.2f}")
    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API : {e}")
