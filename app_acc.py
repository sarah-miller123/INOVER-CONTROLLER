import streamlit as st
import subprocess
import sys
import os
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Tableau de Bord Maintenance", page_icon="🛠️")

# Style CSS avec hauteur fixe pour les cartes
st.markdown("""
<style>
    :root {
        --primary: #1e88e5;
        --secondary: #0d47a1;
        --accent: #ff5722;
        --light: #f5f5f5;
        --dark: #212121;
    }
    
    .main-title {
        font-size: 2.8rem !important;
        color: var(--primary) !important;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        background: linear-gradient(to right, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
    }
    
    .section-title {
        font-size: 1.8rem !important;
        color: var(--secondary) !important;
        border-bottom: 2px solid var(--primary);
        padding-bottom: 8px;
        margin-top: 30px;
    }
    
    .app-card {
        border: none;
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        height: 320px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .app-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(to bottom, var(--primary), var(--accent));
    }
    
    .app-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .app-title {
        color: var(--dark);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .app-description {
        color: #555;
        line-height: 1.6;
        flex-grow: 1;
        overflow: hidden;
    }
    
    .stButton>button {
        border: none;
        background: linear-gradient(to right, var(--primary), var(--secondary));
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
        width: 100%;
        margin-top: auto;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(to right, transparent, var(--primary), transparent);
        margin: 40px 0;
        opacity: 0.3;
    }
    
    .admin-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid var(--accent);
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    
    .animated-icon {
        animation: float 3s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown(
    '<p class="main-title">'
    '<span class="animated-icon">🛠️</span> Tableau de Bord Maintenance Industrielle'
    '</p>', 
    unsafe_allow_html=True
)

# Introduction
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; color: #555; font-size: 1.1rem;">
    Plateforme de surveillance et d'analyse des performances de maintenance<br>
    Visualisation des indicateurs clés et optimisation des processus
</div>
""", unsafe_allow_html=True)

# Cartes d'application
st.markdown('<div class="section-title">📊 Tableaux de Bord Analytiques</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="app-card">
        <h2 class="app-title">⏳ Temps d'Arrêt</h2>
        <p class="app-description">
            Analyse comparative des pannes critiques par durée de défaillance.
            Visualisation hebdomadaire/mensuelle avec tendances et comparaisons périodiques.
            Outil idéal pour identifier les temps d'arrêt les plus impactants.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Temps d'Arrêt", key="btn1"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp.py"])
            st.success("Ouverture en cours...")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

with col2:
    st.markdown("""
    <div class="app-card">
        <h2 class="app-title">📈 Fréquences d'Arrêts</h2>
        <p class="app-description">
            Suivi des occurrences de pannes par équipement.
            Identification des problèmes récurrents et analyse des fréquences.
            Tableaux et graphiques interactifs pour un diagnostic rapide.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Nombres d'Arrêt", key="btn2"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp2.py"])
            st.success("Ouverture en cours...")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

with col3:
    st.markdown("""
    <div class="app-card">
        <h2 class="app-title">📊 KPI Maintenance</h2>
        <p class="app-description">
            Tableau de bord complet des indicateurs clés (MTBF, MTTR, Disponibilité).
            Suivi des tendances et benchmarking des performances.
            Export des données pour reporting.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Indicateurs", key="btn3"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_ind.py"])
            st.success("Ouverture en cours...")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

# Analyse Root Cause - Version avec un seul bouton fonctionnel
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Analyse Root Cause</div>', unsafe_allow_html=True)

# Style CSS (identique à la version précédente)
st.markdown("""
<style>
    .diagnostic-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        margin: 20px 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .diagnostic-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25);
    }
    
    .diagnostic-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1e88e5 0%, #0d47a1 100%);
    }
    
    .diagnostic-title {
        color: #0d47a1;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 15px;
        position: relative;
        display: inline-block;
        width: 100%;
    }
    
    .diagnostic-title::after {
        content: '';
        display: block;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #ff5722 0%, #ff9800 100%);
        margin: 10px auto;
        border-radius: 3px;
    }
    
    .diagnostic-desc {
        color: #455a64;
        line-height: 1.7;
        text-align: center;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
    
    .pulse-effect {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Création des colonnes pour centrer le contenu
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_center:
    # Carte de diagnostic
    st.markdown("""
    <div class="diagnostic-card pulse-effect">
        <h3 class="diagnostic-title">
            <span style="display: inline-block; animation: float 3s ease-in-out infinite;">🔍</span> 
            Diagnostic Complet des Défauts
        </h3>
        <p class="diagnostic-desc">
            Analyse approfondie avec méthode des <strong>5P</strong>, diagrammes <strong>Ishikawa (4M)</strong><br>
            et plan d'action correctif. Identification des causes racines<br>
            et définition d'actions d'amélioration ciblées.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton unique et fonctionnel avec style personnalisé
    st.markdown("""
    <style>
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #1e88e5 0%, #0d47a1 100%);
            border: none;
            color: white;
            padding: 12px 30px;
            text-align: center;
            font-size: 16px;
            margin: 10px auto;
            cursor: pointer;
            border-radius: 50px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
            display: block;
            width: fit-content;
        }
        
        div.stButton > button:first-child:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(30, 136, 229, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Bouton Streamlit fonctionnel
    if st.button("📑 Accéder au Diagnostic Komax", key="btn_analyse"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_accueil.py"])
            st.success("Lancement du module d'analyse...")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")
                
# Section Administration
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚙️ Administration</div>', unsafe_allow_html=True)

with st.expander("Options Administrateur", expanded=False):
    st.markdown("""
    <div class="admin-section">
        <h3 style="color: #d32f2f;">Zone de gestion des données</h3>
        <p style="color: #555;">
            Actions critiques - Réservé aux administrateurs système
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Réinitialiser toutes les données", key="btn_reset"):
        confirm = st.checkbox("Je confirme vouloir réinitialiser toutes les données")
        if confirm:
            if os.path.exists('weekly_data'):
                for f in os.listdir('weekly_data'):
                    os.remove(os.path.join('weekly_data', f))
                os.rmdir('weekly_data')
            st.success("Données réinitialisées avec succès!")
            st.balloons()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #888; font-size: 0.9rem;">
    <hr style="border: 0.5px solid #eee; margin-bottom: 20px;">
    Tableau de Bord Maintenance - Version 2.1 © 2025<br>
    Direction Industrielle | Service Maintenance
</div>
""", unsafe_allow_html=True)
