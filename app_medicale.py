import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import threading
import time
import requests

# --- CONFIGURATION ---
API_URL = "https://sante-app-t2h3.onrender.com"
INSCRIPTION_OUVERTE = True 


def keep_alive():
    while True:
        time.sleep(240)
        try:
            requests.get(f"{API_URL}/public/stats_globales", timeout=5)
        except:
            pass
        
thread = threading.Thread(target=keep_alive, daemon=True)
thread.start()

st.set_page_config(page_title="HealthCollect Pro", page_icon="🏥", layout="wide")

# Actualise l'application automatiquement toutes les 30 secondes
st.empty() # Optionnel
from streamlit_autorefresh import st_autorefresh # Nécessite 'pip install streamlit-autorefresh'
st_autorefresh(interval=30000, key="datarefresh")

# --- STYLE MODERNE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

    /* ===== FOND GÉNÉRAL ===== */
    .stApp {
        background: linear-gradient(160deg, #0f1b2d 0%, #1a2a44 60%, #0d2233 100%);
        font-family: 'Nunito', sans-serif;
        color: #e8edf5;
    }

    /* --- TRANSFORMATION DES TABS EN NAV BAR FLOTTANTE --- */
    .stTabs [data-baseweb="tab-list"] {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
    
        /* Effet Verre Dépoli (Glassmorphism) */
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    
        /* Forme Pilule */
        padding: 8px 20px;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    
        display: flex;
        gap: 15px;
    }

    /* Style des boutons d'onglets individuels */
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
        font-weight: 500;
        padding: 10px 20px !important;
        border-radius: 30px !important;
        transition: all 0.3s ease;
    }

    /* Style de l'onglet actif (Sélectionné) */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Masquer la ligne de soulignement par défaut de Streamlit */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Ajustement pour que le contenu ne soit pas caché sous la barre */
    .stApp {
        margin-top: 80px;
    }
    
    /* ===== EN-TÊTE ===== */
    h1 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        color: #e8edf5 !important;
    }
    p, label, div {
        font-family: 'Nunito', sans-serif !important;
        color: #a8b8cc !important;
    }

    /* ===== ONGLETS (style Makazi) ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
        background-color: rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 6px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        color: #a8b8cc !important;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0 20px;
        background: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }

    /* ===== CARTES (style Makazi — fond sombre arrondi) ===== */
    div[data-testid="metric-container"],
    .stForm,
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        padding: 24px !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px);
    }

    /* ===== MÉTRIQUES ===== */
    div[data-testid="metric-container"] label {
        color: #7fa8cc !important;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #34d399 !important;
        font-weight: 600;
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: #000000 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
    }

    /* ===== BOUTON PRINCIPAL (style "Commencer →" de Makazi) ===== */
    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(37, 99, 235, 0.5) !important;
    }

    /* ===== ALERTES & INFO ===== */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        color: #a8b8cc !important;
    }
    .stSuccess {
        background-color: rgba(52, 211, 153, 0.12) !important;
        border-color: rgba(52, 211, 153, 0.3) !important;
    }
    .stError {
        background-color: rgba(239, 68, 68, 0.12) !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
    }
    .stWarning {
        background-color: rgba(251, 191, 36, 0.10) !important;
        border-color: rgba(251, 191, 36, 0.25) !important;
    }

    /* ===== SÉPARATEUR ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 20px 0 !important;
    }

    /* ===== SIDEBAR (si utilisée) ===== */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 27, 45, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if 'token' not in st.session_state:
    st.session_state.token = None

# --- EN-TÊTE ---
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🏥 Portail HealthCollect</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Système intelligent de collecte et d'analyse de constantes vitales</p>", unsafe_allow_html=True)
st.write("---")

# --- CRÉATION DES ONGLETS ---
tab_public, tab_patient, tab_medecin = st.tabs([
    "🌍 Données Publiques (Statistiques)",
    "📝 Espace Patient (Inscription & Saisie)",
    "🔐 Espace Médecin (Dossiers Privés)"
])

# ==========================================
# ONGLET 1 : DONNÉES PUBLIQUES
# ==========================================
with tab_public:
    st.header("📊 Tendances de Santé Globales")
    st.write("Ces données sont entièrement anonymisées et accessibles à tous pour le suivi de la santé publique.")
   
    # Appel à l'API publique (Si l'API est éteinte, on affiche des valeurs par défaut pour la démo)
    try:
        res_stats = requests.get(f"{API_URL}/public/stats_globales")
        stats = res_stats.json() if res_stats.status_code == 200 else {"temp_moyenne": 37.2, "pouls_moyen": 74, "total_relevés": 0}
    except:
        stats = {"temp_moyenne": 37.2, "pouls_moyen": 74, "total_relevés": "--"}

    # Affichage des métriques de façon moderne
    col1, col2, col3 = st.columns(3)
    col1.metric("Température Moyenne Globale", f"{stats['temp_moyenne']} °C", "Normale")
    col2.metric("Rythme Cardiaque Moyen", f"{stats['pouls_moyen']} BPM", "Stable")
    col3.metric("Relevés Enregistrés", f"{stats['total_relevés']}", "Aujourd'hui")

 

    st.subheader("📊 Tableau de bord de santé publique")

    # --- LIGNE 1 : 2 Gauges (Température + BPM) ---
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_temp = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stats['temp_moyenne'],
            delta={"reference": 37.0, "valueformat": ".1f"},
            number={"suffix": " °C", "font": {"size": 40, "color": "#ffffff"}},
            gauge={
                "axis": {"range": [35, 42], "tickcolor": "#a8b8cc"},
                "bar": {"color": "#2563eb", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(255,255,255,0.1)",
                "steps": [
                    {"range": [35, 36.5], "color": "rgba(59,130,246,0.2)"},
                    {"range": [36.5, 37.5], "color": "rgba(52,211,153,0.3)"},
                    {"range": [37.5, 42],  "color": "rgba(239,68,68,0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.75,
                    "value": 38
                }
            },
            title={"text": "Température Moyenne", "font": {"color": "#a8b8cc", "size": 14}}
        ))
        fig_temp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#ffffff"},
            height=250,
            margin=dict(t=60, b=20, l=30, r=30)
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_g2:
        fig_bpm = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stats['pouls_moyen'],
            delta={"reference": 70, "valueformat": ".0f"},
            number={"suffix": " BPM", "font": {"size": 40, "color": "#ffffff"}},
            gauge={
                "axis": {"range": [40, 180], "tickcolor": "#a8b8cc"},
                "bar": {"color": "#0ea5e9", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(255,255,255,0.1)",
                "steps": [
                    {"range": [40, 60],  "color": "rgba(59,130,246,0.2)"},
                    {"range": [60, 100], "color": "rgba(52,211,153,0.3)"},
                    {"range": [100, 180],"color": "rgba(239,68,68,0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.75,
                    "value": 100
                }
            },
            title={"text": "Rythme Cardiaque Moyen", "font": {"color": "#a8b8cc", "size": 14}}
        ))
        fig_bpm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#ffffff"},
            height=250,
            margin=dict(t=60, b=20, l=30, r=30)
        )
        st.plotly_chart(fig_bpm, use_container_width=True)

    # --- LIGNE 2 : Bar chart volume + Line chart tendance ---
    col_b1, col_b2 = st.columns(2)

    def get_stats_globales():
        """Récupère les statistiques depuis le backend"""
        try:
            # On appelle la route publique de ton API
            response = requests.get(f"{API_URL}/public/stats_globales", timeout=5)
            if response.status_code == 200:
                return response.json(), True
            return {}, False
        except Exception as e:
            st.error(f"Erreur de connexion au backend : {e}")
            return {}, False
    
    with col_b1:
        st.markdown("**🔍 Dispersion Température / Rythme Cardiaque (données publiques)**")
    
        # Récupérer toutes les mesures via les stats globales
        stats_raw, ok = get_stats_globales()
       
        try:
            res_mesures = requests.get(
                f"{API_URL}/public/toutes_mesures", timeout=5
            )
            if res_mesures.status_code == 200:
                df_scatter_pub = pd.DataFrame(res_mesures.json())
                source_scatter = "✅ Données réelles"
            else:
                raise Exception()
        except:
            # Données simulées si API indisponible
            np.random.seed(42)
            n = 30
            df_scatter_pub = pd.DataFrame({
                "temperature": np.round(
                    np.random.normal(37.1, 0.5, n).clip(35, 42), 1
                ),
                "rythme_cardiaque": np.random.randint(55, 130, n)
            })
            source_scatter = "⚠️ Données simulées"
    
        st.caption(source_scatter)
    
        if not df_scatter_pub.empty:
            # Droite de tendance (régression linéaire)
            x = df_scatter_pub["temperature"]
            y = df_scatter_pub["rythme_cardiaque"]
            coeffs = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = np.polyval(coeffs, x_line)
            df_tendance = pd.DataFrame({
                "temperature": x_line,
                "tendance": y_line
            })
    
            fig_scatter_pub = px.scatter(
                df_scatter_pub,
                x="temperature",
                y="rythme_cardiaque",
                color="rythme_cardiaque",
                color_continuous_scale=["#34d399", "#2563eb", "#ef4444"],
                labels={
                    "temperature": "Température (°C)",
                    "rythme_cardiaque": "Rythme Cardiaque (BPM)"
                },
                title="Corrélation Température / Cardio"
            )
    
            # Ajout droite de tendance
            fig_scatter_pub.add_scatter(
                x=x_line, y=y_line,
                mode="lines",
                name="Tendance",
                line=dict(color="#f59e0b", width=2, dash="dash")
            )
    
            # Lignes seuils
            fig_scatter_pub.add_vline(
                x=37.5, line_dash="dash",
                line_color="#ef4444", opacity=0.5,
                annotation_text="Seuil fièvre",
                annotation_font_color="#ef4444"
            )
            fig_scatter_pub.add_hline(
                y=100, line_dash="dash",
                line_color="#f59e0b", opacity=0.5,
                annotation_text="Tachycardie",
                annotation_font_color="#f59e0b"
            )
    
            fig_scatter_pub.update_traces(
                marker=dict(size=10, opacity=0.8,
                           line=dict(width=1, color="rgba(255,255,255,0.3)")),
                selector=dict(mode="markers")
            )
            fig_scatter_pub.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#a8b8cc"},
                title_font_color="#ffffff",
                coloraxis_showscale=False,
                height=280,
                margin=dict(t=40, b=20, l=20, r=20),
                xaxis=dict(
                    gridcolor="rgba(255,255,255,0.05)",
                    title="Température (°C)",
                    range=[35, 42]
                ),
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.05)",
                    title="BPM"
                ),
                showlegend=True,
                legend=dict(
                    font=dict(color="#a8b8cc"),
                    bgcolor="rgba(0,0,0,0)"
                )
            )
            st.plotly_chart(fig_scatter_pub, use_container_width=True)

    with col_b2:
        st.markdown("**Tendance température (30 derniers jours)**")
        import numpy as np
        jours = list(range(1, 31))
        temps_data = [round(37.0 + np.random.uniform(-0.4, 0.6), 1) for _ in jours]
        df_trend = pd.DataFrame({"Jour": jours, "Température": temps_data})

        fig_line = px.area(
            df_trend, x="Jour", y="Température",
            color_discrete_sequence=["#2563eb"]
        )
        fig_line.add_hline(
            y=37.5, line_dash="dash",
            line_color="#ef4444", opacity=0.6,
            annotation_text="Seuil fièvre",
            annotation_font_color="#ef4444"
        )
        fig_line.update_traces(
            fill="tozeroy",
            fillcolor="rgba(37,99,235,0.15)",
            line=dict(color="#2563eb", width=2)
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#a8b8cc"},
            height=280,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Jour du mois"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[36, 39])
        )
        st.plotly_chart(fig_line, use_container_width=True)
# ==========================================
# ONGLET 2 : ESPACE PATIENT (SAISIE COMPLÈTE)
# ==========================================
with tab_patient:
    st.header("Créer mon dossier et transmettre mes constantes")
    st.info("Aucun compte n'est requis. Vos données seront transmises de manière sécurisée à l'équipe médicale.")
   
    with st.form("form_patient_complet"):
        st.subheader("👤 Informations Personnelles")
        col_a, col_b = st.columns(2)
        with col_a:
            nom = st.text_input("Nom Complet *")
            email = st.text_input("Adresse Email *")
            age = st.number_input("Âge *", min_value=1, max_value=120)
        with col_b:
            genre = st.selectbox("Sexe", ["Masculin", "Féminin", "Autre"])
            poids = st.number_input("Poids (kg)", min_value=10.0, step=0.5)
            groupe = st.selectbox("Groupe Sanguin", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Inconnu"])
       
        st.write("---")
        st.subheader("🩺 Mes Constantes du Jour")
        col_c, col_d = st.columns(2)
        with col_c:
            temp = st.number_input("Température (°C) *", min_value=30.0, max_value=45.0, value=37.0, step=0.1)
        with col_d:
            cardio = st.number_input("Rythme Cardiaque (BPM) *", min_value=30, max_value=250, value=70)
       
        submit_btn = st.form_submit_button("Enregistrer et Transmettre")
       
        if submit_btn:
            if not nom or not email:
                st.error("Veuillez remplir les champs obligatoires (*).")
            else:
                # 1. Création du dossier patient via l'API publique
                patient_data = {
                    "nom_complet": nom, "email": email, "age": age,
                    "genre": genre, "poids": poids, "groupe_sanguin": groupe,
                    "temperature": temp, "rythme_cardiaque":cardio
                }
                try:
                    res_pat = requests.post(f"{API_URL}/public/enregistrer_dossier/", json=patient_data)
                   
                    if res_pat.status_code == 200 or res_pat.status_code == 400:
                        # Si le patient est créé (200) ou existe déjà (400), on tente d'enregistrer la mesure
                        # Note : Pour un vrai système, on récupèrerait l'ID exact via l'email
                        st.success(f"Dossier validé pour {nom}.")
                       
                        # (Logique simplifiée pour la démo, on suppose que le backend associe la mesure via email ou ID)
                        st.success(f"✅ Vos constantes ({temp}°C, {cardio} BPM) ont été transmises avec succès !")
                    else:
                        st.error("Erreur lors de la création du dossier.")
                except:
                    st.error("Le serveur API est injoignable.")

# ==========================================
# ONGLET 3 : ESPACE MÉDECIN (SÉCURISÉ)
# ==========================================
with tab_medecin:

     if not st.session_state.token:
        st.warning("⚠️ Accès restreint au personnel médical.")
        col_log1, col_log2, col_log3 = st.columns([1, 2, 1])
       
        with col_log2:
            
            with st.form("form_connexion"):
                st.subheader("Authentification Sécurisée")
                username = st.text_input("Identifiant Médecin")
                password = st.text_input("Mot de passe", type="password")
                btn_login = st.form_submit_button("Se Connecter")
               
                if btn_login:
                    res_auth = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
                    if res_auth.status_code == 200:
                        st.session_state.token = res_auth.json()["access_token"]
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")
                else:
                    # Interface si le médecin est connecté
                    col_head1, col_head2 = st.columns([4, 1])
                    col_head1.header("👨‍⚕️ Dossiers Patients Privés")
                    if col_head2.button("Se déconnecter"):
                        st.session_state.token = None
                        st.rerun()
                       
                    st.write("---")
                   
                    patient_id = st.number_input("Entrez l'identifiant (ID) du patient à consulter", min_value=1, step=1)
       
        if st.button("Afficher le dossier médical"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            # Appel à la route sécurisée !
            res_dossier = requests.get(f"{API_URL}/medecin/patient/{patient_id}", headers=headers)
           
            if res_dossier.status_code == 200:
                p = res_dossier.json()
               
                # Affichage des infos personnelles chiffrées/protégées
                st.markdown(f"### 📋 Patient : **{p['nom_complet']}**")
                c1, c2, c3 = st.columns(3)
                c1.info(f"Âge : {p['age']} ans | Sexe : {p['genre']}")
                c2.info(f"Poids : {p['poids']} kg | Groupe : {p['groupe_sanguin']}")
                c3.info(f"Contact : {p['email']}")
               
                # Génération des graphiques Plotly
                if p.get('mesures'):
                    df = pd.DataFrame(p['mesures'])
                    df['date_prise'] = pd.to_datetime(df['date_prise'])
                    df = df.sort_values('date_prise')
                   
                    col_priv1, col_priv2 = st.columns(2)

                    with col_priv1:
                        # Line chart température
                        fig_temp_priv = px.line(
                            df, x='date_prise', y='temperature',
                            markers=True, title="🌡️ Évolution Température"
                        )
                        fig_temp_priv.add_hline(
                            y=37.5, line_dash="dash",
                            line_color="#ef4444", opacity=0.7,
                            annotation_text="Seuil fièvre 37.5°C",
                            annotation_font_color="#ef4444"
                        )
                        fig_temp_priv.update_traces(
                            line=dict(color="#2563eb", width=2.5),
                            marker=dict(color="#0ea5e9", size=8)
                        )
                        fig_temp_priv.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font={"color": "#a8b8cc"},
                            title_font_color="#ffffff",
                            height=300,
                            margin=dict(t=50, b=20, l=20, r=20),
                            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Date"),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="°C", range=[35, 42])
                        )
                        st.plotly_chart(fig_temp_priv, use_container_width=True)

                    with col_priv2:
                        # Area chart rythme cardiaque
                        fig_cardio_priv = px.area(
                            df, x='date_prise', y='rythme_cardiaque',
                            title="❤️ Rythme Cardiaque"
                        )
                        fig_cardio_priv.add_hline(
                            y=100, line_dash="dash",
                            line_color="#f59e0b", opacity=0.7,
                            annotation_text="Seuil tachycardie",
                            annotation_font_color="#f59e0b"
                        )
                        fig_cardio_priv.update_traces(
                            fill="tozeroy",
                            fillcolor="rgba(14,165,233,0.15)",
                            line=dict(color="#0ea5e9", width=2.5)
                        )
                        fig_cardio_priv.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font={"color": "#a8b8cc"},
                            title_font_color="#ffffff",
                            height=300,
                            margin=dict(t=50, b=20, l=20, r=20),
                            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Date"),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="BPM")
                        )
                        st.plotly_chart(fig_cardio_priv, use_container_width=True)

                    # Scatter anomalies
                    st.markdown("**🔍 Détection d'anomalies**")
                    fig_scatter = px.scatter(
                        df, x='temperature', y='rythme_cardiaque',
                        color='temperature',
                        color_continuous_scale=["#34d399", "#2563eb", "#ef4444"],
                        size_max=15,
                        hover_data=['date_prise'],
                        title="Corrélation Température / Cardio"
                    )
                    fig_scatter.add_vline(x=37.5, line_dash="dash", line_color="#ef4444", opacity=0.5)
                    fig_scatter.add_hline(y=100,  line_dash="dash", line_color="#f59e0b", opacity=0.5)
                    fig_scatter.update_traces(marker=dict(size=10, opacity=0.8))
                    fig_scatter.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font={"color": "#a8b8cc"},
                        title_font_color="#ffffff",
                        height=350,
                        margin=dict(t=50, b=20, l=20, r=20),
                        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Température (°C)"),
                        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="BPM"),
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.warning("Aucune constante enregistrée pour ce patient.")
            else:
                st.error("Dossier introuvable ou vous n'avez pas les autorisations nécessaires.")
