import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta
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
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<p class="main-title">Analyse Comparative des Top 3 Pannes</p>', unsafe_allow_html=True)

# Fonction améliorée pour traiter les fichiers Excel
def process_file(file, week_num):
    try:
        # Lecture avec gestion des erreurs de format
        df = pd.read_excel(file, header=9, usecols='B:X')
        
        # Vérification des colonnes nécessaires
        if 'Type Of Failure' not in df.columns or 'Down Time' not in df.columns:
            st.error("Le fichier Excel ne contient pas les colonnes requises.")
            return None
            
        # Nettoyage des données
        df = df.dropna(how='all', axis=1)
        df['Type Of Failure'] = df['Type Of Failure'].str.strip()
        
        # Filtrage
        mask = ~df['Type Of Failure'].isin(['DEMARRAGE PARC', 'PREVENTIVE MAINTENANCE'])
        df = df[mask].copy()
        
        if not df.empty:
            df = df.iloc[:-1]  # Supprimer la dernière ligne seulement si le DataFrame n'est pas vide
            
        # Conversion des temps
        try:
            df['Down Time'] = pd.to_datetime(df['Down Time'], format="%H:%M:%S").dt.time
            df['Down Time'] = df['Down Time'].apply(lambda x: x.hour + x.minute/60 + x.second/3600)
        except:
            st.warning("Format de temps incorrect - utilisation des valeurs brutes")
            df['Down Time'] = pd.to_numeric(df['Down Time'], errors='coerce')
        
        # Ajout des métadonnées temporelles
        df['Semaine'] = f"Semaine {week_num}"
        
        # Date et mois
        year = datetime.now().year
        week_start = datetime.strptime(f"{year}-W{week_num}-1", "%Y-W%W-%w")
        df['Mois'] = (week_start + timedelta(weeks=(week_num-1)//4)).strftime('%Y-%m')  # Groupe par mois de 4 semaines
        
        return df.dropna(subset=['Type Of Failure', 'Down Time'])
    except Exception as e:
        st.error(f"Erreur critique lors du traitement: {str(e)}")
        return None

# Fonction pour sauvegarder avec vérification
def save_week_data(week_num, df):
    try:
        if not os.path.exists('weekly_data'):
            os.makedirs('weekly_data')
        
        if df is not None and not df.empty:
            save_path = f'weekly_data/week_{week_num}.pkl'
            df.to_pickle(save_path)
            return True
        return False
    except:
        return False

# Fonction pour charger les données avec vérification
def load_historical_data(weeks_back=12):
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
                        data[f"Semaine {week_num}"] = df
                except:
                    continue
    except:
        pass
    return data

# Interface utilisateur
with st.sidebar:
    st.header("Configuration")
    current_week = st.number_input("Numéro de semaine", min_value=1, max_value=52, 
                                 value=datetime.now().isocalendar()[1])
    current_file = st.file_uploader("Importer le fichier Excel", type=['xlsx'])
    
    # Ajout du temps d'ouverture
    TO = st.number_input("Temps d'ouverture (heures)", min_value=1, value=8235, 
                       help="Durée totale de la période analysée en heures")
    
    if st.button("Traiter la semaine") and current_file:
        with st.spinner('Traitement en cours...'):
            df = process_file(current_file, current_week)
            if df is not None and not df.empty:
                # Ajout du TO aux données
                df['TO'] = TO
                if save_week_data(current_week, df):
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
    # Préparation des données avec vérification
    comparison_data = []
    for week_name, df in historical_data.items():
        if not df.empty and 'Type Of Failure' in df.columns and 'Down Time' in df.columns:
            top_pannes = df.groupby('Type Of Failure')['Down Time'].sum().nlargest(3).reset_index()
            if not top_pannes.empty:
                top_pannes['Semaine'] = week_name
                comparison_data.append(top_pannes)
    
    if not comparison_data:
        st.error("Aucune donnée valide pour la comparaison")
        st.stop()
    
    comparison_df = pd.concat(comparison_data, ignore_index=True)
    
    # Création du graphique
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Couleurs pour top 1, 2, 3
    
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

# Affichage des tableaux détaillés avec vérification
st.header("Détails par Mois")

# Sélection de mois à afficher
months = sorted(set([df['Mois'].iloc[0] for df in historical_data.values() if 'Mois' in df.columns]), reverse=True)
selected_month = st.selectbox("Sélectionner un mois", months)

for month in months:
    if selected_month == month:
        monthly_data = [df for week_name, df in historical_data.items() if 'Mois' in df.columns and df['Mois'].iloc[0] == month]
        month_df = pd.concat(monthly_data, ignore_index=True)
        
        if not month_df.empty and 'Type Of Failure' in month_df.columns and 'Down Time' in month_df.columns:
            top_pannes = month_df.groupby('Type Of Failure')['Down Time'].sum().nlargest(3).reset_index()
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
                        title=f"Répartition - {month}",
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                except:
                    st.warning("Impossible de créer le camembert pour ce mois")

# Section des indicateurs clés
st.header("Indicateurs Clés")

try:
    metrics = []
    for week_name, df in historical_data.items():
        if not df.empty and 'Down Time' in df.columns and 'TO' in df.columns:
            TO = df['TO'].iloc[0]  # Temps d'ouverture
            TA = df['Down Time'].sum()  # Temps d'arrêt
            NB = df['Down Time'].count()  # Nombre d'occurrences
            
            # Calcul des indicateurs
            mtbf = (TO - TA) / NB if NB > 0 else 0
            mttr = TA / NB if NB > 0 else 0
            disponibilite = ((TO - TA) / TO) * 100 if TO > 0 else 0
            
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
        
        # Affichage du tableau
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
        
        # Légende
        st.markdown("""
        **Définitions:**
        - **MTBF:** Temps moyen entre deux pannes = (Temps d'ouverture - Temps d'arrêt) / Nombre d'occurrences
        - **MTTR:** Temps moyen de réparation = Temps d'arrêt total / Nombre d'occurrences
        - **Disponibilité:** Pourcentage de temps de fonctionnement = ((TO - TA) / TO) × 100
        """)
        
        # Graphique d'évolution MTBF/MTTR
        st.header("Évolution MTBF/MTTR")
        
        MTBF_objectif = 8.5  # Valeur cible MTBF
        MTTR_objectif = 0.08  # Valeur cible MTTR
        
        fig_mtbf_mttr = go.Figure()
        
        # MTBF
        fig_mtbf_mttr.add_trace(go.Scatter(
            x=metrics_df['Semaine'],
            y=metrics_df['MTBF (h)'],
            name='MTBF Réalisé',
            line=dict(color='green', width=2),
            mode='lines+markers'
        ))
        
        # Objectif MTBF
        fig_mtbf_mttr.add_trace(go.Scatter(
            x=metrics_df['Semaine'],
            y=[MTBF_objectif]*len(metrics_df),
            name='Objectif MTBF',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        # MTTR
        fig_mtbf_mttr.add_trace(go.Scatter(
            x=metrics_df['Semaine'],
            y=metrics_df['MTTR (h)'],
            name='MTTR Réalisé',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        # Objectif MTTR
        fig_mtbf_mttr.add_trace(go.Scatter(
            x=metrics_df['Semaine'],
            y=[MTTR_objectif]*len(metrics_df),
            name='Objectif MTTR',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig_mtbf_mttr.update_layout(
            title='Évolution MTBF et MTTR vs Objectifs',
            xaxis_title='Semaine',
            yaxis_title='Heures',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_mtbf_mttr, use_container_width=True)
        
        # Graphique d'évolution de la disponibilité
        st.header("Évolution de la Disponibilité")
        
        disponibilite_objectif = 98  # Objectif de disponibilité en %
        
        fig_dispo = go.Figure()
        
        # Barres de disponibilité
        couleurs = []
        for dispo in metrics_df['Disponibilité (%)']:
            if dispo >= disponibilite_objectif:
                couleurs.append('green')
            elif dispo >= disponibilite_objectif - 5:
                couleurs.append('orange')
            else:
                couleurs.append('red')
        
        fig_dispo.add_trace(go.Bar(
            x=metrics_df['Semaine'],
            y=metrics_df['Disponibilité (%)'],
            marker_color=couleurs,
            name='Disponibilité',
            text=metrics_df['Disponibilité (%)'].round(1).astype(str) + '%',
            textposition='auto'
        ))
        
        # Ligne d'objectif
        fig_dispo.add_trace(go.Scatter(
            x=metrics_df['Semaine'],
            y=[disponibilite_objectif]*len(metrics_df),
            name='Objectif',
            line=dict(color='blue', width=2, dash='dash')
        ))
        
        fig_dispo.update_layout(
            title='Évolution de la Disponibilité vs Objectif',
            xaxis_title='Semaine',
            yaxis_title='Disponibilité (%)',
            yaxis_range=[0, 110],
            height=500
        )
        
        st.plotly_chart(fig_dispo, use_container_width=True)
        
    else:
        st.warning("Aucun indicateur calculable")
        
except Exception as e:
    st.error(f"Erreur lors du calcul des indicateurs: {str(e)}")

# Bouton de réinitialisation
if st.sidebar.button("🔄 Réinitialiser COMPLÈTEMENT l'application"):
    # Supprimer les fichiers temporaires
    if os.path.exists('weekly_data'):
        for f in os.listdir('weekly_data'):
            os.remove(os.path.join('weekly_data', f))
        os.rmdir('weekly_data')
    
    # Réinitialiser le cache de Streamlit
    st.cache_data.clear()
    
    # Réinitialiser l'état de session
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("Application complètement réinitialisée! Rechargez la page.")
    st.experimental_rerun()