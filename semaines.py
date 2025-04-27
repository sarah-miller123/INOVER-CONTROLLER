import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(layout="wide", page_title="Analyse Comparative des Pannes")

# Style CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem !important;
        color: #1e88e5 !important;
        text-align: center;
        margin-bottom: 30px;
    }
    .sidebar-input {
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<p class="main-title">Analyse Comparative des Top 3 Pannes</p>', unsafe_allow_html=True)

# Fonction améliorée pour traiter les fichiers Excel
def process_file(file):
    try:
        df = pd.read_excel(file, header=9, usecols='B:X')
        if 'Type Of Failure' not in df.columns or 'Down Time' not in df.columns:
            st.error("Le fichier Excel ne contient pas les colonnes requises.")
            return None
            
        df = df.dropna(how='all', axis=1)
        df['Type Of Failure'] = df['Type Of Failure'].str.strip()
        
        mask = ~df['Type Of Failure'].isin(['DEMARRAGE PARC', 'PREVENTIVE MAINTENANCE'])
        df = df[mask].copy()
        
        if not df.empty:
            df = df.iloc[:-1]
            
        try:
            df['Down Time'] = pd.to_datetime(df['Down Time'], format="%H:%M:%S").dt.time
            df['Down Time'] = df['Down Time'].apply(lambda x: x.hour + x.minute/60 + x.second/3600)
        except:
            st.warning("Format de temps incorrect - utilisation des valeurs brutes")
            df['Down Time'] = pd.to_numeric(df['Down Time'], errors='coerce')
        
        return df.dropna(subset=['Type Of Failure', 'Down Time'])
    except Exception as e:
        st.error(f"Erreur critique lors du traitement: {str(e)}")
        return None

def save_week_data(week_num, df, TO):
    try:
        if not os.path.exists('weekly_data'):
            os.makedirs('weekly_data')
        
        if df is not None and not df.empty:
            # Ajouter le TO aux données sauvegardées
            df['TO'] = TO
            save_path = f'weekly_data/week_{week_num}.pkl'
            df.to_pickle(save_path)
            return True
        return False
    except:
        return False

def load_historical_data(weeks_back=3):
    data = {}
    try:
        if os.path.exists('weekly_data'):
            files = sorted([f for f in os.listdir('weekly_data') if f.startswith('week_') and f.endswith('.pkl')], 
                          key=lambda x: int(x.split('_')[1].split('.')[0]), 
                          reverse=True)
            
            for f in files[:weeks_back]:
                try:
                    week_num = f.split('_')[1].split('.')[0]
                    df = pd.read_pickle(f'weekly_data/{f}')
                    if not df.empty:
                        # Récupérer le TO sauvegardé
                        TO = df['TO'].iloc[0] if 'TO' in df.columns else 168
                        df = df.drop(columns=['TO'], errors='ignore')
                        data[f"Semaine {week_num}"] = {'df': df, 'TO': TO}
                except:
                    continue
    except:
        pass
    return data

# Interface utilisateur
with st.sidebar:
    st.header("Configuration")
    
    current_week = st.number_input(
        "Numéro de semaine", 
        min_value=1, 
        max_value=52, 
        value=datetime.now().isocalendar()[1],
        key="num_semaine"
    )
    
    current_file = st.file_uploader(
        "Importer le fichier Excel", 
        type=['xlsx'],
        key="file_uploader"
    )
    
    if current_file:
        TO = st.number_input(
            f"Temps d'ouverture (heures) - Semaine {current_week}", 
            min_value=1,
            value=8235,
            step=1,
            help="Durée totale de la période analysée en heures",
            key=f"temps_ouverture_{current_week}",
            format="%d"
        )
    
    if st.button("Traiter la semaine") and current_file:
        with st.spinner('Traitement en cours...'):
            df = process_file(current_file)
            if df is not None and not df.empty:
                if save_week_data(current_week, df, TO):
                    st.success(f"Données de la semaine {current_week} sauvegardées!")
                else:
                    st.warning("Erreur lors de la sauvegarde")
            else:
                st.error("Aucune donnée valide à sauvegarder")

# Chargement des données
historical_data = load_historical_data()

if not historical_data:
    st.warning("Aucune donnée historique valide trouvée. Veuillez importer des données.")
    st.stop()

# Section d'analyse comparative
st.header("Comparaison des Top 3 Pannes")

try:
    comparison_data = []
    for week_name, week_data in historical_data.items():
        df = week_data['df']
        if not df.empty and 'Type Of Failure' in df.columns and 'Down Time' in df.columns:
            top_pannes = df.groupby('Type Of Failure')['Down Time'].sum().nlargest(3).reset_index()
            if not top_pannes.empty:
                top_pannes['Semaine'] = week_name
                comparison_data.append(top_pannes)
    
    if not comparison_data:
        st.error("Aucune donnée valide pour la comparaison")
        st.stop()
    
    comparison_df = pd.concat(comparison_data, ignore_index=True)
    
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for rank in range(1, 4):
        rank_data = []
        for week_name in historical_data.keys():
            week_df = comparison_df[comparison_df['Semaine'] == week_name]
            if len(week_df) >= rank:
                rank_data.append({
                    'Semaine': week_name,
                    'Type': week_df.iloc[rank-1]['Type Of Failure'],
                    'Temps': week_df.iloc[rank-1]['Down Time'],
                    'Rank': f"Top {rank}"
                })
        
        if rank_data:
            rank_df = pd.DataFrame(rank_data)
            fig.add_trace(go.Bar(
                x=rank_df['Semaine'],
                y=rank_df['Temps'],
                name=f'Top {rank}',
                marker_color=colors[rank-1],
                text=rank_df['Type'],
                textposition='auto',
                hoverinfo='text+y',
                hovertext=rank_df.apply(lambda row: f"{row['Type']}<br>{row['Temps']:.2f} heures", axis=1)
            ))

    fig.update_layout(
        barmode='group',
        title=f"Comparaison des Top 3 Pannes sur {len(historical_data)} Semaines",
        xaxis_title="Semaine",
        yaxis_title="Temps d'arrêt (heures)",
        hovermode="x unified",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erreur lors de la création du graphique: {str(e)}")

# Affichage des tableaux détaillés
st.header("Détails par Semaine")

for week_name, week_data in historical_data.items():
    df = week_data['df']
    TO = week_data['TO']
    with st.expander(f"Détails - {week_name} (TO: {TO} heures)"):
        if not df.empty and 'Type Of Failure' in df.columns and 'Down Time' in df.columns:
            top_pannes = df.groupby('Type Of Failure')['Down Time'].sum().nlargest(3).reset_index()
            top_pannes['Pourcentage'] = (top_pannes['Down Time'] / top_pannes['Down Time'].sum()) * 100
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(
                    top_pannes.style.format({
                        'Down Time': '{:.2f} heures',
                        'Pourcentage': '{:.1f}%'
                    }), 
                    height=200,
                    hide_index=True
                )
            
            with col2:
                try:
                    fig_pie = px.pie(
                        top_pannes, 
                        values='Down Time', 
                        names='Type Of Failure', 
                        title=f"Répartition - {week_name}",
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                except:
                    st.warning("Impossible de créer le camembert pour cette semaine")
        else:
            st.warning(f"Données incomplètes pour {week_name}")

# Section des indicateurs
st.header("Indicateurs Clés")

try:
    metrics = []
    for week_name, week_data in historical_data.items():
        df = week_data['df']
        TO = week_data['TO']
        
        if not df.empty and 'Down Time' in df.columns:
            TA = df['Down Time'].sum()
            NB = df['Down Time'].count()
            
            mtbf = (TO - TA) / NB if NB > 0 else 0
            mttr = TA / NB if NB > 0 else 0
            disponibilite = ((TO - TA) / TO) * 100
            
            metrics.append({
                'Semaine': week_name,
                'Temps Ouverture (h)': TO,
                'Temps Arrêt (h)': TA,
                'Nb Occurrences': NB,
                'MTBF (h)': mtbf,
                'MTTR (h)': mttr,
                'Disponibilité (%)': disponibilite
            })
    
    if metrics:
        metrics_df = pd.DataFrame(metrics)
        
        st.dataframe(
            metrics_df.style.format({
                'Temps Ouverture (h)': '{:.0f}',
                'Temps Arrêt (h)': '{:.2f}',
                'MTBF (h)': '{:.2f}',
                'MTTR (h)': '{:.2f}',
                'Disponibilité (%)': '{:.1f}%'
            }), 
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("""
        **Définitions:**
        - **MTBF:** Temps moyen entre deux pannes = (Temps d'ouverture - Temps d'arrêt) / Nombre d'occurrences
        - **MTTR:** Temps moyen de réparation = Temps d'arrêt total / Nombre d'occurrences
        - **Disponibilité:** Pourcentage de temps de fonctionnement
        """)
    else:
        st.warning("Aucun indicateur calculable")
except Exception as e:
    st.error(f"Erreur lors du calcul des indicateurs: {str(e)}")

# Graphique combiné MTBF/MTTR
st.header("Évolution MTBF/MTTR")

MTBF_objectif = 8.5
MTTR_objectif = 0.08

try:
    if metrics:
        compare_df = pd.DataFrame(metrics)[['Semaine', 'MTBF (h)', 'MTTR (h)']].copy()

        fig = go.Figure()

        # Courbe MTBF Réalisé
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=compare_df['MTBF (h)'],
            mode='lines+markers',
            name='MTBF Réalisé',
            line=dict(color='green')
        ))

        # Courbe MTBF Objectif
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=[MTBF_objectif]*len(compare_df),
            mode='lines',
            name='MTBF Objectif',
            line=dict(color='green', dash='dash')
        ))

        # Courbe MTTR Réalisé
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=compare_df['MTTR (h)'],
            mode='lines+markers',
            name='MTTR Réalisé',
            line=dict(color='red')
        ))

        # Courbe MTTR Objectif
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=[MTTR_objectif]*len(compare_df),
            mode='lines',
            name='MTTR Objectif',
            line=dict(color='red', dash='dash')
        ))

        fig.update_layout(
            title="Évolution MTBF et MTTR (Réalisés vs Objectifs)",
            xaxis_title="Semaine",
            yaxis_title="Valeurs (heures)",
            legend_title="Indicateur",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"Erreur dans l'affichage du graphique combiné : {e}")

# Graphique d'évolution de la disponibilité
st.header("Évolution de la Disponibilité")

disponibilite_objectif = 98  # Objectif global de disponibilité

try:
    if metrics:
        # Créer un DataFrame à partir des métriques
        compare_df = pd.DataFrame(metrics)
        
        # Définir les couleurs selon les critères
        couleurs = []
        for valeur in compare_df['Disponibilité (%)']:
            if valeur < disponibilite_objectif - 5:
                couleurs.append('red')  # Loin de l'objectif
            elif disponibilite_objectif - 5 <= valeur < disponibilite_objectif:
                couleurs.append('orange')  # Proche de l'objectif
            else:
                couleurs.append('green')  # Atteint ou dépasse l'objectif

        # Création du graphique avec Plotly
        fig = go.Figure()
        
        # Ajouter les barres de disponibilité
        fig.add_trace(go.Bar(
            x=compare_df['Semaine'],
            y=compare_df['Disponibilité (%)'],
            marker_color=couleurs,
            name='Disponibilité Réalisée',
            text=compare_df['Disponibilité (%)'].round(1).astype(str) + '%',
            textposition='auto'
        ))
        
        # Ajouter la ligne d'objectif
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=[disponibilite_objectif]*len(compare_df),
            mode='lines',
            name=f'Objectif ({disponibilite_objectif}%)',
            line=dict(color='blue', dash='dash')
        ))
        
        # Mise en forme du graphique
        fig.update_layout(
            title='Comparaison de la Disponibilité Réalisée vs Objectif',
            yaxis_title='Disponibilité (%)',
            yaxis_range=[0, 110],
            hovermode="x unified",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
except Exception as e:
    st.error(f"Erreur lors de la création du graphique de disponibilité: {str(e)}")
# Bouton de réinitialisation
if st.sidebar.button("🔄 Réinitialiser COMPLÈTEMENT l'application"):
    if os.path.exists('weekly_data'):
        for f in os.listdir('weekly_data'):
            os.remove(os.path.join('weekly_data', f))
        os.rmdir('weekly_data')
    
    st.cache_data.clear()
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("Application complètement réinitialisée! Rechargez la page.")
    st.experimental_rerun()