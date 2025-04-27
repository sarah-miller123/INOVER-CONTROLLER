# -*- coding: utf-8 -*-
import streamlit as st
import os
from streamlit.runtime.scriptrunner import RerunData, RerunException
from streamlit.source_util import get_pages

# Configuration de base
st.set_page_config(
    layout="wide",
    page_title="Tableau de Bord Maintenance",
    page_icon="🛠️",
    initial_sidebar_state="collapsed"
)

# ===================================================
# VOTRE CSS COMPLET (CONSERVÉ À L'IDENTIQUE)
# ===================================================
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
    
    /* ... (TOUT VOTRE CSS EXISTANT RESTE ICI) ... */
    
    .animated-icon {
        animation: float 3s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)
# ===================================================

# Fonction de navigation optimisée pour Streamlit Share
def switch_page(page_name: str):
    """Fonction pour changer de page sans subprocess"""
    pages = get_pages("app_acc.py")
    for page_hash, config in pages.items():
        if config["page_name"] == page_name:
            raise RerunException(
                RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )
    st.error(f"Impossible de trouver la page '{page_name}'")

# ===================================================
# VOTRE CONTENU PRINCIPAL (CONSERVÉ À L'IDENTIQUE)
# ===================================================
st.markdown(
    '<p class="main-title">'
    '<span class="animated-icon">🛠️</span> Tableau de Bord Maintenance Industrielle'
    '</p>', 
    unsafe_allow_html=True
)

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
        <h2 class="app-title">⏳ Cartographie des Temps d'Arrêt</h2>
        <p class="app-description">
            Analyse comparative des pannes critiques par durée d'indisponibilité.
            Visualisation hebdomadaire/mensuelle avec tendances et comparaisons périodiques.
            Outil idéal pour identifier les temps d'arrêt les plus impactants.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Temps d'Arrêt", key="btn1"):
        switch_page("app_comp")  # Navigation modifiée ici

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
        switch_page("app_comp2")  # Navigation modifiée ici

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
        switch_page("app_ind")  # Navigation modifiée ici

# ===================================================
# GESTION DES PAGES (NOUVEAU - À GARDER À LA FIN)
# ===================================================
if "current_page" in st.session_state:
    if st.session_state.current_page == "app_comp":
        switch_page("app_comp")
    elif st.session_state.current_page == "app_comp2":
        switch_page("app_comp2")
    elif st.session_state.current_page == "app_ind":
        switch_page("app_ind")
    elif st.session_state.current_page == "app_accueil":
        switch_page("app_accueil")

# Footer (conservé)
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #888; font-size: 0.9rem;">
    <hr style="border: 0.5px solid #eee; margin-bottom: 20px;">
    Tableau de Bord Maintenance - Version 2.1 © 2025<br>
    Direction Industrielle | Service Maintenance
</div>
""", unsafe_allow_html=True)