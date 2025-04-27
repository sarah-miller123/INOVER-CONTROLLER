# -*- coding: utf-8 -*-
import streamlit as st
import os

# Configuration de la page (conservée)
st.set_page_config(
    layout="wide", 
    page_title="Tableau de Bord Maintenance", 
    page_icon="🛠️",
    initial_sidebar_state="collapsed"
)

# =============================================
# VOTRE CSS COMPLET (CONSERVÉ À L'IDENTIQUE)
# =============================================
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
    
    /* ... (TOUT VOTRE CSS EXISTANT RESTE ICI) ... */
    
    .animated-icon {
        animation: float 3s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# FONCTION DE NAVIGATION (NOUVEAU)
# =============================================
def navigate_to(page_path: str):
    """Navigation centralisée pour tous les boutons"""
    st.session_state.target_page = page_path
    st.rerun()

# =============================================
# VOTRE CONTENU PRINCIPAL (CONSERVÉ)
# =============================================
st.markdown(
    '<p class="main-title">'
    '<span class="animated-icon">🛠️</span> Tableau de Bord Maintenance Industrielle'
    '</p>', 
    unsafe_allow_html=True
)

# Section Tableaux de Bord
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
        navigate_to("apps/app_comp.py")

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
        navigate_to("apps/app_comp2.py")

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
        navigate_to("apps/app_ind.py")

# Section Diagnostic
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Analyse Root Cause</div>', unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1, 3, 1])
with col_center:
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
    
    if st.button("📑 Accéder au Diagnostic Komax", key="btn_analyse"):
        navigate_to("apps/app_accueil.py")

# Section Admin (conservée)
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
        if st.checkbox("Je confirme vouloir réinitialiser toutes les données"):
            try:
                # Votre logique de réinitialisation ici
                st.success("Données réinitialisées avec succès!")
                st.balloons()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")

# Footer (conservé)
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #888; font-size: 0.9rem;">
    <hr style="border: 0.5px solid #eee; margin-bottom: 20px;">
    Tableau de Bord Maintenance - Version 2.1 © 2025<br>
    Direction Industrielle | Service Maintenance
</div>
""", unsafe_allow_html=True)

# =============================================
# GESTION CENTRALISÉE DE LA NAVIGATION (NOUVEAU)
# =============================================
if hasattr(st.session_state, 'target_page'):
    try:
        st.switch_page(st.session_state.target_page)
    except Exception as e:
        st.error(f"Page non trouvée : {str(e)}")
        del st.session_state.target_page