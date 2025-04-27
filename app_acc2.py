import streamlit as st
import subprocess
import sys
import os

st.set_page_config(layout="wide", page_title="Tableau de Bord Maintenance")

# Style CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem !important;
        color: #1e88e5 !important;
        text-align: center;
        margin-bottom: 30px;
    }
    .app-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s;
    }
    .app-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .app-title {
        color: #1e88e5;
        font-size: 1.5rem;
    }
    .app-description {
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<p class="main-title">Tableau de Bord Maintenance</p>', unsafe_allow_html=True)

# Cartes d'application
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="app-card">
        <h2 class="app-title">⏳ Cartographie des Temps d'Arrêt Critiques</h2>
        <p class="app-description">Comparaison des principales pannes selon leurs temps d'Arrêt sur plusieurs semaines et analyse détaillée par semaine/mois.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Temps d'Arrêt", key="btn1"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp.py"])
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

with col2:
    st.markdown("""
    <div class="app-card">
        <h2 class="app-title">🛠️ Bilan Maintenance : Fréquences d'Arrêts</h2>
        <p class="app-description">Comparaison des principales pannes selon leurs nombres d'Arrêt sur plusieurs semaines et analyse détaillée par semaine/mois.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Nombres d'Arrêt", key="btn2"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp2.py"])
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

with col3:
    st.markdown("""
    <div class="app-card">
        <h2 class="app-title">📊 Analyse des Indicateurs</h2>
        <p class="app-description">Suivi des indicateurs clés (MTBF, MTTR, Disponibilité) et évolution temporelle.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ouvrir l'Analyse des Indicateurs", key="btn3"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_ind.py"])
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

# Section Analyse Causes & Actions
st.markdown("---")
st.subheader("🔍 Analyse des Causes & Actions")

if st.button("📑 Accéder au Diagnostique Complet des Défauts Komax", key="btn_analyse"):
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_accueil.py"])
        st.success("Ouverture de l'analyse complète...")
    except Exception as e:
        st.error(f"Erreur : {str(e)}")

# Section administration
st.markdown("---")
st.subheader("Administration")

if st.button("🔄 Réinitialiser toutes les données"):
    if os.path.exists('weekly_data'):
        for f in os.listdir('weekly_data'):
            os.remove(os.path.join('weekly_data', f))
        os.rmdir('weekly_data')
    st.success("Données réinitialisées avec succès!")