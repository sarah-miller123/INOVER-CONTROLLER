import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from datetime import datetime
import sys
import subprocess

st.set_page_config(layout="wide", page_title="Analyse des Indicateurs")

# Style CSS étendu
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
        border-left: 5px solid #1e88e5;
    }
    .stMetric {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric > div {
        margin-bottom: 5px;
    }
    .stMetricLabel {
        font-weight: bold;
        color: #1e88e5;
    }
    .stMetricValue {
        font-size: 1.5rem;
    }
    .stAlert {
        border-radius: 10px;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    h2 {
        color: #1e88e5 !important;
        border-bottom: 2px solid #1e88e5;
        padding-bottom: 5px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal avec icône
st.markdown('<p class="main-title">📈 Analyse des Indicateurs Clés</p>', unsafe_allow_html=True)

def load_historical_data(weeks_back=26):
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
                        TO = df['TO'].iloc[0] if 'TO' in df.columns else 8235
                        data[f"Semaine {week_num}"] = {'df': df, 'TO': TO}
                except Exception as e:
                    st.warning(f"Fichier {f} corrompu ou incompatible : {str(e)}")
                    continue
    except Exception as e:
        st.error(f"Erreur lors du chargement des données historiques : {str(e)}")
    return data

with st.sidebar:
    st.header("🔀 Navigation")
    
    if st.button("🏠 Retour à l'accueil"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_acc.py"])
            st.stop()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

    if st.button("⏱️ Voir Analyse des Temps d'Arrêt"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp.py"])
            st.stop()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

    if st.button("🔢 Voir Analyse des Nombre d'Arrêts"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp2.py"])
            st.stop()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

    st.markdown("---")
    st.header("⚙️ Paramètres")
    
    weeks_back = st.slider(
        "Nombre de semaines à analyser",
        min_value=4,
        max_value=52,
        value=12,
        help="Nombre de semaines à inclure dans l'analyse historique"
    )
    
    MTBF_objectif = st.number_input(
        "Objectif MTBF (heures)",
        min_value=0.0,
        value=8.5,
        step=0.1,
        help="Valeur cible pour le MTBF"
    )
    
    MTTR_objectif = st.number_input(
        "Objectif MTTR (heures)",
        min_value=0.0,
        value=0.08,
        step=0.01,
        format="%.2f",
        help="Valeur cible pour le MTTR"
    )
    
    Disp_objectif = st.number_input(
        "Objectif Disponibilité (%)",
        min_value=0.0,
        max_value=100.0,
        value=98.0,
        step=0.1,
        help="Valeur cible pour la Disponibilité"
    )

# Chargement des données avec indicateur visuel
with st.spinner(f'Chargement des données sur {weeks_back} semaines...'):
    historical_data = load_historical_data(weeks_back)

if not historical_data:
    st.warning("⚠️ Aucune donnée historique valide trouvée. Veuillez importer des données dans l'application d'analyse comparative.")
    st.stop()

# Section des indicateurs clés
st.header("📊 Indicateurs Clés de Performance")

try:
    # Préparation des données
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
        
        # Dernières valeurs pour les métriques
        last_week = metrics_df.iloc[0]
        
        # Tableau des données avec mise en forme conditionnelle
        st.markdown("### Détail par semaine")
        
        def color_negative_red(val, threshold):
            color = 'red' if val < threshold else 'green'
            return f'color: {color}'
        
        styled_df = metrics_df.style.format({
            'Temps Ouverture (h)': '{:.0f}',
            'Temps Arrêt (h)': '{:.2f}',
            'MTBF (h)': '{:.2f}',
            'MTTR (h)': '{:.2f}',
            'Disponibilité (%)': '{:.1f}%'
        }).applymap(lambda x: color_negative_red(x, MTBF_objectif), subset=['MTBF (h)']) \
          .applymap(lambda x: color_negative_red(x, Disp_objectif), subset=['Disponibilité (%)']) \
          .applymap(lambda x: color_negative_red(-x, -MTTR_objectif), subset=['MTTR (h)'])
        
        st.dataframe(styled_df, height=400, use_container_width=True)
        
        # Bouton d'export
        if st.button("📤 Exporter les données au format Excel"):
            try:
                with pd.ExcelWriter('indicateurs_maintenance.xlsx') as writer:
                    metrics_df.to_excel(writer, sheet_name='Indicateurs', index=False)
                st.success("Fichier Excel généré avec succès!")
                st.download_button(
                    label="⬇️ Télécharger le fichier",
                    data=open('indicateurs_maintenance.xlsx', 'rb').read(),
                    file_name='indicateurs_maintenance.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                st.error(f"Erreur lors de l'export : {str(e)}")

    else:
        st.warning("⚠️ Aucun indicateur calculable")
except Exception as e:
    st.error(f"❌ Erreur lors du calcul des indicateurs: {str(e)}")

# Graphique combiné MTBF/MTTR
st.header("📈 Évolution MTBF/MTTR")

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
            line=dict(color='green', width=3),
            marker=dict(size=8, color='green'),
            hovertemplate='%{x}<br>MTBF: %{y:.2f}h'
        ))

        # Courbe MTBF Objectif
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=[MTBF_objectif]*len(compare_df),
            mode='lines',
            name='MTBF Objectif',
            line=dict(color='green', dash='dash', width=2),
            hovertemplate='Objectif: %{y:.2f}h'
        ))

        # Courbe MTTR Réalisé (sur axe secondaire)
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=compare_df['MTTR (h)'],
            mode='lines+markers',
            name='MTTR Réalisé',
            line=dict(color='red', width=3),
            marker=dict(size=8, color='red'),
            hovertemplate='%{x}<br>MTTR: %{y:.2f}h',
            yaxis='y2'
        ))

        # Courbe MTTR Objectif (sur axe secondaire)
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=[MTTR_objectif]*len(compare_df),
            mode='lines',
            name='MTTR Objectif',
            line=dict(color='red', dash='dash', width=2),
            hovertemplate='Objectif: %{y:.2f}h',
            yaxis='y2'
        ))

        # Calcul des échelles des axes
        max_mtbf = max(compare_df['MTBF (h)'].max(), MTBF_objectif) * 1.1
        max_mttr = max(compare_df['MTTR (h)'].max(), MTTR_objectif) * 1.5

        fig.update_layout(
            title="Évolution MTBF et MTTR (Réalisés vs Objectifs)",
            xaxis_title="Semaine",
            yaxis_title="MTBF (heures)",
            yaxis=dict(range=[0, max_mtbf]),
            yaxis2=dict(
                title="MTTR (heures)",
                overlaying='y',
                side='right',
                range=[0, max_mttr],
                showgrid=False
            ),
            legend_title="Indicateur",
            hovermode="x unified",
            height=500,
            plot_bgcolor='rgba(240,242,246,0.8)',
            paper_bgcolor='rgba(240,242,246,0.5)',
            xaxis=dict(tickangle=45),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Erreur dans l'affichage du graphique combiné : {e}")

# Graphique d'évolution de la disponibilité
st.header("📊 Évolution de la Disponibilité")

try:
    if metrics:
        compare_df = pd.DataFrame(metrics)
        
        # Définir les couleurs selon les critères
        couleurs = []
        for valeur in compare_df['Disponibilité (%)']:
            if valeur < Disp_objectif - 5:
                couleurs.append('red')  # Loin de l'objectif
            elif Disp_objectif - 5 <= valeur < Disp_objectif:
                couleurs.append('orange')  # Proche de l'objectif
            else:
                couleurs.append('green')  # Atteint ou dépasse l'objectif

        # Création du graphique
        fig = go.Figure()
        
        # Ajouter les barres de disponibilité
        fig.add_trace(go.Bar(
            x=compare_df['Semaine'],
            y=compare_df['Disponibilité (%)'],
            marker_color=couleurs,
            name='Disponibilité Réalisée',
            text=compare_df['Disponibilité (%)'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto',
            marker_line=dict(width=1, color='DarkSlateGrey'),
            hovertemplate='%{x}<br>Disponibilité: %{y:.1f}%'
        ))
        
        # Ajouter la ligne d'objectif
        fig.add_trace(go.Scatter(
            x=compare_df['Semaine'],
            y=[Disp_objectif]*len(compare_df),
            mode='lines',
            name=f'Objectif ({Disp_objectif}%)',
            line=dict(color='blue', dash='dash', width=2),
            hovertemplate='Objectif: %{y}%'
        ))

        # Mise en forme du graphique
        fig.update_layout(
            title='Comparaison de la Disponibilité Réalisée vs Objectif',
            yaxis_title='Disponibilité (%)',
            yaxis_range=[max(0, compare_df['Disponibilité (%)'].min() - 5), min(100, compare_df['Disponibilité (%)'].max() + 5)],
            hovermode="x unified",
            height=500,
            plot_bgcolor='rgba(240,242,246,0.8)',
            paper_bgcolor='rgba(240,242,246,0.5)',
            xaxis=dict(tickangle=45),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse de la disponibilité
        st.markdown("### Analyse de la disponibilité")
        
        last_4_weeks = compare_df.head(4)
        avg_disp = last_4_weeks['Disponibilité (%)'].mean()
        disp_trend = (last_4_weeks['Disponibilité (%)'].iloc[0] - last_4_weeks['Disponibilité (%)'].iloc[-1]) / last_4_weeks['Disponibilité (%)'].iloc[-1] * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Disponibilité moyenne (4 semaines)",
                f"{avg_disp:.1f}%",
                delta=f"Objectif: {Disp_objectif}%",
                delta_color="inverse" if avg_disp < Disp_objectif else "normal"
            )
        
        with col2:
            st.metric(
                "Tendance (4 semaines)",
                f"{disp_trend:.1f}%",
                help="Variation de la disponibilité sur les 4 dernières semaines"
            )
        
        # Alertes
        if avg_disp < Disp_objectif - 2:
            st.error("🔴 Alerte: Disponibilité en dessous des objectifs - Analyse requise")
        elif avg_disp < Disp_objectif:
            st.warning("🟠 Attention: Disponibilité proche des objectifs - Surveillance requise")
        else:
            st.success("🟢 Bonne nouvelle: Disponibilité conforme ou supérieure aux objectifs")
        
except Exception as e:
    st.error(f"❌ Erreur lors de la création du graphique de disponibilité: {str(e)}")