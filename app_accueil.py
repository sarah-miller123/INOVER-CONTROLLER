# -*- coding: utf-8 -*-
import streamlit as st
import subprocess
import sys
from streamlit.components.v1 import html

def main():
    # Configuration premium de la page
    st.set_page_config(
        page_title="Diagnostique Komax - Causes & Solutions",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS premium avec animations
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
        
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --accent: #f59e0b;
            --dark: #1e293b;
            --light: #f8fafc;
        }
        
        * {
            font-family: 'Montserrat', sans-serif;
        }
        
        .main {
            background: radial-gradient(circle at 10% 20%, rgba(248, 250, 252, 0.9) 0%, rgba(226, 232, 240, 0.9) 90%);
        }
        
        .hero {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
        }
        
        .title {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            font-size: 1.25rem;
            font-weight: 300;
            opacity: 0.9;
            margin: 0.5rem 0 0 0;
        }
        
        .method-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin: 3rem auto;
            max-width: 1200px;
        }
        
        .method-card {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-top: 4px solid var(--accent);
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .method-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        
        .method-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: var(--primary);
        }
        
        .method-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--dark);
            margin: 0 0 1rem 0;
        }
        
        .method-desc {
            color: #64748b;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            text-align: center;
            flex-grow: 1;
        }
        
        .method-btn-container {
            margin-top: auto;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px rgba(37, 99, 235, 0.2);
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.875rem;
            margin-top: 4rem;
            border-top: 1px solid #e2e8f0;
        }
        
        /* Assure que toutes les colonnes ont la même hauteur */
        [data-testid="column"] {
            display: flex;
            flex-direction: column;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Section Hero premium
    st.markdown("""
    <div class="hero">
        <h1 class="title">📊 Diagnostique Complet des Défauts Komax : Analyse des Causes et Plans Correctifs</h1>
        <p class="subtitle">🛠️ Une solution intégrée pour identifier les racines des problèmes et mettre en œuvre les actions correctives</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Description
    st.markdown("""
    <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left: 5px solid #4e73df;'>
    <h3 style='color:#2e59d9; text-align:center;'>🔍 Votre Centre d'Analyse Komax 🔍</h3>
    <p style='text-align:center; font-size:16px; color:#5a5c69;'>
    <b>Explorez l'intelligence industrielle sous tous ses angles :</b>
    </p>

    <ul style='color:#5a5c69; font-size:15px;'>
    <li>📊 <b>Vue complète</b> - Tous les tableaux 5P à portée de main</li>
    <li>🛠️ <b>Actions concrètes</b> - Le plan d'action détaillé prêt à l'emploi</li>
    <li>🎯 <b>Focus expert</b> - Analyse ciblée avec :<br>
        ▸ 5P personnalisé du défaut<br>
        ▸ Solution intégrée clé en main<br>
        ▸ Diagramme Ishikawa interactif</li>
    </ul>

    <p style='text-align:center; font-style:italic; color:#4e73df; margin-top:15px;'>
    Sélectionnez votre mode d'analyse pour une prise de décision éclairée !
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section Méthodes avec descriptions harmonisées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="method-card">
            <div class="method-icon">📋</div>
            <h3 class="method-title">Méthode 5P</h3>
            <p class="method-desc">
                Accédez à l'ensemble des tableaux 5P complets pour tous les composants.
                Vue globale idéale pour une analyse et un suivi qualité.
            </p>
            <div class="method-btn-container">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(
            "Accéder aux tableaux 5P",
            help="Cliquez pour voir tous les tableaux 5P",
            key="btn_5p"
        ):
            launch_analysis("app_5p_folder.py")
    
    with col2:
        st.markdown("""
        <div class="method-card">
            <div class="method-icon">📌</div>
            <h3 class="method-title">Analyse 4M Ishikawa</h3>
            <p class="method-desc">
                Analyse ciblée d'un défaut spécifique avec son diagramme causes-effet,
                sa fiche 5P détaillée et les solutions associées extraites du plan global.
            </p>
            <div class="method-btn-container">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(
            "Lancer l'analyse Focus",
            help="Cliquez pour analyser avec la méthode des 4M",
            key="btn_4m"
        ):
            launch_analysis("app_4m_folder.py")
    
    with col3:
        st.markdown("""
        <div class="method-card">
            <div class="method-icon">✅</div>
            <h3 class="method-title">Plan d'Action</h3>
            <p class="method-desc">
                Consultez l'intégralité du plan d'action correctif.
                Suivi des tâches, responsables et échéances pour une résolution efficace.
            </p>
            <div class="method-btn-container">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(
            "Voir le plan d'action",
            help="Cliquez pour accéder au plan d'action complet",
            key="btn_plan_action"
        ):
            launch_analysis("app_plan_action_folder.py")
    
    # Pied de page premium
    st.markdown("""
    <div class="footer">
        <p>© 2025 - Département Maintenance Industrielle Komax</p>
        <p style="font-size: 0.75rem; opacity: 0.7;">Système d'Analyse des Causes Racines v2.0</p>
    </div>
    """, unsafe_allow_html=True)

def launch_analysis(script_name):
    """Lance le script d'analyse spécifié"""
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", script_name])
        st.stop()  # Arrête l'exécution de l'app courante
    except Exception as e:
        st.error(f"Erreur technique: {str(e)}")
        st.info("Veuillez contacter le support technique")

if __name__ == "__main__":
    main()