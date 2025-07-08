# frontend/app_streamlit.py

import os
import streamlit as st
import requests

st.set_page_config(
    page_title="Prédiction Maladie Cardiaque",
    layout="wide"
)

# --- Header principal centré ---
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0;">
      <h1 style="color: #d6336c;">💓 Prédiction de maladie cardiaque 💓</h1>
      <p style="font-size:16px; color:gray">
        Saisissez vos identifiants, renseignez les paramètres, puis cliquez sur « Prédire »
      </p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

# --- Barre latérale : authentification + formulaire patient ---
with st.sidebar:
    st.header("🔐 Authentification")
    username = st.text_input("Nom d'utilisateur", value="admin")
    password = st.text_input("Mot de passe", type="password", value="monpassword")

    st.header("🔧 Paramètres du patient")
    age      = st.slider("Âge", 1, 120, 63)
    sex_map  = {0: "Femme", 1: "Homme"}
    sex      = st.selectbox("Sexe", list(sex_map.keys()), format_func=lambda x: sex_map[x])
    cp       = st.selectbox("Type de douleur thoracique (cp)", [0,1,2,3])
    trestbps = st.number_input("Tension artérielle (mmHg)", 80, 200, 145)
    chol     = st.number_input("Cholestérol (mg/dl)", 100, 400, 233)
    fbs_map  = {0: "Non", 1: "Oui"}
    fbs      = st.selectbox("Glycémie à jeun >120mg/dl", [0,1], format_func=lambda x: fbs_map[x])
    restecg  = st.selectbox("ECG au repos", [0,1,2])
    thalach  = st.number_input("Fréq. cardiaque max", 50, 250, 150)
    exang_map= {0: "Non", 1: "Oui"}
    exang    = st.selectbox("Angine induite par effort", [0,1], format_func=lambda x: exang_map[x])
    oldpeak  = st.slider("Oldpeak (dépression ST)", 0.0, 6.0, 2.3, step=0.1)
    slope    = st.selectbox("Slope du segment ST", [0,1,2])
    ca       = st.selectbox("Nombre de vaisseaux colorés", [0,1,2,3,4])
    thal_map = {0:"Normal",1:"Fixed",2:"Reversible"}
    thal     = st.selectbox("Thal", [0,1,2], format_func=lambda x: thal_map[x])

    submitted = st.button("🚀 Prédire")

result_placeholder = st.empty()

if submitted:
    API_URL = st.secrets.get("general", {}).get("API_URL") or os.getenv("API_URL")
    if not API_URL:
        result_placeholder.error("API_URL non configurée !")
        st.stop()

    # Authentification pour obtenir le token
    with result_placeholder.container():
        with st.spinner("🔑 Authentification..."):
            try:
                resp = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )
                resp.raise_for_status()
                token = resp.json().get("access_token")
                if not token:
                    st.error("Impossible de récupérer le jeton JWT.")
                    st.stop()
            except Exception as e:
                st.error(f"Erreur lors de l'authentification : {e}")
                st.stop()

        # Préparation des données et requête de prédiction
        payload = {
            "age": age,
            "sex": sex,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": restecg,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": slope,
            "ca": ca,
            "thal": thal,
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        with st.spinner("🩺 Calcul en cours..."):
            try:
                res = requests.post(f"{API_URL}/predict", json=payload, headers=headers, timeout=10)
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                st.error(f"Erreur lors de l'appel API : {e}")
                st.stop()

        # Affichage dynamique des résultats et conseils
        st.markdown("---")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if data["prediction"] == 0:
                titre = "<h2 style='color:#198754'>✔️ Absence de maladie cardiaque détectée</h2>"
                conseils = """
                <div style='background:#e7f5ec;padding:18px 25px 15px 25px;border-radius:15px;margin-bottom:18px;'>
                <b>Conseils pour rester en bonne santé :</b>
                <ul style="text-align:left; font-size:16px;">
                  <li>Continuez à adopter une alimentation saine et équilibrée.</li>
                  <li>Pratiquez une activité physique régulière.</li>
                  <li>Évitez le tabac et limitez l’alcool.</li>
                  <li>Contrôlez votre tension et votre cholestérol.</li>
                  <li>Pensez à des bilans réguliers, surtout après 40 ans.</li>
                </ul>
                </div>
                """
            else:
                titre = "<h2 style='color:#d6336c'>⚠️ Risque de maladie cardiaque détecté</h2>"
                conseils = """
                <div style='background:#fff4f0;padding:18px 25px 15px 25px;border-radius:15px;margin-bottom:18px;'>
                <b>Conseils importants :</b>
                <ul style="text-align:left; font-size:16px;">
                  <li>Consultez rapidement un professionnel de santé.</li>
                  <li>Faites un bilan cardiaque approfondi.</li>
                  <li>Adoptez sans attendre une alimentation pauvre en sel et en graisses saturées.</li>
                  <li>Arrêtez de fumer et limitez strictement l’alcool.</li>
                  <li>Pratiquez une activité adaptée sur avis médical.</li>
                </ul>
                </div>
                """

            st.markdown(titre, unsafe_allow_html=True)
            st.metric("📈 Probabilité", f"{data['probability']*100:.1f} %")
            st.markdown(conseils, unsafe_allow_html=True)
            st.success("✅ Prédiction terminée !")
