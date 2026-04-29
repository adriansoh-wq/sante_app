import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# L'adresse de votre API FastAPI
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Health Dashboard", page_icon="🏥", layout="wide")
st.title("🏥 Tableau de Bord Médical")

# --- BARRE LATÉRALE : AUTHENTIFICATION ---
st.sidebar.header("Connexion")
username = st.sidebar.text_input("Utilisateur")
password = st.sidebar.text_input("Mot de passe", type="password")

if st.sidebar.button("Se connecter"):
    # On demande un Token à l'API
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        st.session_state['token'] = response.json()["access_token"]
        st.sidebar.success("Connecté !")
    else:
        st.sidebar.error("Identifiants incorrects")

# --- ZONE PRINCIPALE : AFFICHAGE DES DONNÉES ---
if 'token' in st.session_state:
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
   
    st.markdown("---")
    patient_id = st.number_input("Entrez l'ID du patient à consulter :", min_value=1, step=1)
   
    if st.button("Charger le dossier"):
        # Requête à l'API pour récupérer les données du patient
        res = requests.get(f"{API_URL}/patients/{patient_id}", headers=headers)
       
        if res.status_code == 200:
            patient_data = res.json()
            st.subheader(f"Dossier Patient : {patient_data['nom_complet']} (Groupe: {patient_data['groupe_sanguin']})")
           
            mesures = patient_data.get("mesures", [])
           
            if mesures:
                # Transformation des données JSON en tableau (DataFrame) pour faciliter les graphiques
                df = pd.DataFrame(mesures)
                df['date_prise'] = pd.to_datetime(df['date_prise'])
                df = df.sort_values("date_prise")
               
                # Mise en page en deux colonnes
                col1, col2 = st.columns(2)
               
                with col1:
                    # Graphique de la température (Courbe)
                    fig_temp = px.line(
                        df, x='date_prise', y='temperature',
                        title="Évolution de la Température (°C)",
                        markers=True, line_shape="spline" # spline rend la courbe plus douce (créatif)
                    )
                    # Ajout d'une ligne rouge pour le seuil de fièvre
                    fig_temp.add_hline(y=38.0, line_dash="dash", line_color="red", annotation_text="Seuil Fièvre")
                    st.plotly_chart(fig_temp, use_container_width=True)
               
                with col2:
                    # Graphique du rythme cardiaque (Barres)
                    fig_cardio = px.bar(
                        df, x='date_prise', y='rythme_cardiaque',
                        title="Rythme Cardiaque (BPM)",
                        color='rythme_cardiaque', color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_cardio, use_container_width=True)
                   
            else:
                st.info("Aucune constante vitale enregistrée pour ce patient.")
        else:
            st.warning("Patient introuvable ou accès refusé.")
else:
    st.info("Veuillez vous connecter via la barre latérale pour accéder aux données.")