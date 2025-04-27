import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta
import os
import sys
import subprocess

# Configuration de la page
st.set_page_config(layout="wide", page_title="Analyse des Pannes selon Temps d'Arret")

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
        border-left: 5px solid #1e88e5;
    }
    .stExpander > div > div {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
    }
    .stSelectbox > div > div {
        font-size: 1.1rem;
    }
    .stButton > button {
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    h2 {
        color: #1e88e5 !important;
        border-bottom: 2px solid #1e88e5;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<p class="main-title">⏱️ Rapport Maintenance : Analyse Stratégique des Temps Arrêt</p>', unsafe_allow_html=True)

# Fonction pour traiter les fichiers Excel
def process_file(file, week_num):
    try:
        df = pd.read_excel(file, header=9, usecols='B:X')
        if 'Type Of Failure' not in df.columns or 'Down Time' not in df.columns:
            st.error("Le fichier Excel ne contient pas les colonnes requises.")
            return None
            
        df = df.dropna(how='all', axis=1)
        df['Type Of Failure'] = df['Type Of Failure'].str.strip().str.upper()
        
        mask = ~df['Type Of Failure'].isin(['DEMARRAGE PARC', 'PREVENTIVE MAINTENANCE', 'N/A', ''])
        df = df[mask].copy()
        
        if not df.empty:
            df = df.iloc[:-1]
            
        try:
            if pd.api.types.is_object_dtype(df['Down Time']):
                df['Down Time'] = pd.to_datetime(df['Down Time'], format="%H:%M:%S").dt.time
                df['Down Time'] = df['Down Time'].apply(lambda x: x.hour + x.minute/60 + x.second/3600)
        except:
            st.warning("Format de temps incorrect - utilisation des valeurs brutes")
            df['Down Time'] = pd.to_numeric(df['Down Time'], errors='coerce')
        
        df['Semaine'] = f"Semaine {week_num}"
        year = datetime.now().year
        week_start = datetime.strptime(f"{year}-W{week_num}-1", "%Y-W%W-%w")
        df['Mois'] = (week_start + timedelta(weeks=(week_num-1)//4)).strftime('%Y-%m')
        
        return df.dropna(subset=['Type Of Failure', 'Down Time'])
    except Exception as e:
        st.error(f"Erreur lors du traitement: {str(e)}")
        return None

def save_week_data(week_num, df, TO):
    try:
        if not os.path.exists('weekly_data'):
            os.makedirs('weekly_data')
        
        if df is not None and not df.empty:
            df['TO'] = TO
            save_path = f'weekly_data/week_{week_num}.pkl'
            df.to_pickle(save_path)
            return True
        return False
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {str(e)}")
        return False

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
                        TO = df['TO'].iloc[0] if 'TO' in df.columns else 8235
                        df = df.drop(columns=['TO'], errors='ignore')
                        data[f"Semaine {week_num}"] = {'df': df, 'TO': TO}
                except:
                    continue
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
    return data

# Interface utilisateur
with st.sidebar:
    st.header("⚙️ Configuration")
    current_week = st.number_input("Numéro de semaine", min_value=1, max_value=52, 
                                 value=datetime.now().isocalendar()[1])
    current_file = st.file_uploader("Importer le fichier Excel", type=['xlsx'])
    
    TO = st.number_input("Temps d'ouverture (heures)", min_value=1, value=8235)
    
    if st.button("Traiter la semaine") and current_file:
        with st.spinner('Traitement en cours...'):
            df = process_file(current_file, current_week)
            if df is not None and not df.empty:
                if save_week_data(current_week, df, TO):
                    st.success(f"Données de la semaine {current_week} sauvegardées!")
                else:
                    st.warning("Erreur lors de la sauvegarde")
            else:
                st.error("Aucune donnée valide à sauvegarder")

    if st.button("🏠 Retour à l'accueil"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_acc.py"])
            st.stop()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

    if st.button("🔢 Voir Analyse des Nombre d'Arrêts"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_comp2.py"])
            st.stop()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

    if st.button("📊 Voir les indicateurs"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_ind.py"])
            st.stop()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

# Chargement des données
historical_data = load_historical_data()

if not historical_data:
    st.warning("Aucune donnée historique valide trouvée. Veuillez importer des données.")
    st.stop()

# Section pour l'analyse par semaine spécifique
st.header("🔍 Analyse détaillée par semaine")
selected_week = st.selectbox("Choisir une semaine à analyser", sorted(historical_data.keys()))

if selected_week in historical_data:
    week_data = historical_data[selected_week]
    df_week = week_data['df']
    TO_week = week_data['TO']
    
    with st.expander(f"Détails - {selected_week} (TO: {TO_week:.0f} heures)", expanded=True):
        if not df_week.empty and 'Type Of Failure' in df_week.columns and 'Down Time' in df_week.columns:
            df1 = df_week.dropna(how='all', axis=1).copy()
            
            if not pd.api.types.is_numeric_dtype(df1['Down Time']):
                try:
                    df1['Down Time'] = pd.to_datetime(df1['Down Time'], format="%H:%M:%S")
                    df1['Down Time'] = df1['Down Time'].dt.hour + df1['Down Time'].dt.minute/60 + df1['Down Time'].dt.second/3600
                except:
                    df1['Down Time'] = pd.to_numeric(df1['Down Time'], errors='coerce')
            
            if 'Delay Time' in df1.columns:
                if not pd.api.types.is_numeric_dtype(df1['Delay Time']):
                    try:
                        df1['Delay Time'] = pd.to_datetime(df1['Delay Time'], format="%H:%M:%S")
                        df1['Delay Time'] = df1['Delay Time'].dt.hour + df1['Delay Time'].dt.minute/60 + df1['Delay Time'].dt.second/3600
                    except:
                        pass
                df1['T, I'] = df1['Down Time'] - df1['Delay Time']
            
            TA = df1['Down Time'].sum()
            NB = df1['Down Time'].count()
            mtbf = (TO_week - TA) / NB if NB > 0 else 0
            mttr = TA / NB if NB > 0 else 0
            racio = (TA / TO_week) * 100
            Di = ((TO_week - TA) / TO_week) * 100

            if 'Delay Time' in df1.columns:
                retart = df1['Delay Time'].sum()
            else:
                retart = 0
                
            macro_arrêt = df1[df1['Down Time'] >= (10 / 60)]['Down Time'].sum()
            micro_arrêt = df1[df1['Down Time'] < (10 / 60)]['Down Time'].sum()

            st.markdown("#### Indicateurs de performance globaux ")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Temps d'arrêt total (TA)", f"{TA:.2f} heures")
            with col2:
                st.metric("MTBF", f"{mtbf:.2f} heures")
            with col3:
                st.metric("MTTR", f"{mttr:.2f} heures")
            with col4:
                st.metric("Disponibilité", f"{Di:.1f}%")

            df_repartition_TA = pd.DataFrame({
                'Type': ['Retart', 'Macro-arrêt', 'Micro-arrêt'],
                'Temps': [retart, macro_arrêt, micro_arrêt]
            })
            fig_pie = px.pie(df_repartition_TA, values='Temps', names='Type', title='Répartition des temps d\'arrêt')
            fig_pie.update_traces(textinfo='percent+value', texttemplate='%{label}<br>%{value:.2f}h (%{percent})')
            st.plotly_chart(fig_pie, use_container_width=True)

            if 'Machine' in df1.columns:
                df_komax = df1[df1['Machine'].str.contains('KOMAX', na=False)]
                if not df_komax.empty:
                    df_grouped = df_komax.groupby(['Machine', 'Type Of Failure'])['Down Time'].sum().reset_index()
                    df_grouped = df_grouped[df_grouped['Down Time'] > 0]
                    df_totals = df_grouped.groupby('Machine')['Down Time'].sum().reset_index().rename(columns={'Down Time': 'Total'})
                    df_final = df_grouped.merge(df_totals, on='Machine')
                    df_final = df_final.sort_values(by='Total', ascending=False)

                    fig_stacked = px.bar(df_final, x='Machine', y='Down Time', color='Type Of Failure',
                                         title='Temps d\'arrêt par machine KOMAX et type de panne',
                                         labels={'Down Time': 'Temps d\'arrêt (heures)', 'Machine': 'Machine'},
                                         text=df_final['Down Time'].apply(lambda x: f"{x:.2f}"))
                    fig_stacked.update_traces(texttemplate='%{text}', textposition='outside')
                    st.plotly_chart(fig_stacked, use_container_width=True)

                    if 'T, I' in df1.columns:
                        df_komax_indicateurs = df1[df1['Machine'].str.contains('KOMAX', na=False)].copy()

                        df_indicateurs_komax = df_komax_indicateurs.groupby('Machine').agg({
                            'Down Time': 'sum',
                            'Delay Time': 'sum',
                            'T, I': 'sum',
                            'Type Of Failure': 'count'
                        }).reset_index().rename(columns={'Type Of Failure': 'NB'})

                        df_indicateurs_melted = df_indicateurs_komax.melt(id_vars='Machine', 
                                                                  value_vars=['Down Time', 'Delay Time', 'T, I', 'NB'],
                                                                  var_name='Indicateur',
                                                                  value_name='Valeur')

                        fig_comparatif = px.bar(df_indicateurs_melted, 
                                        x='Machine', 
                                        y='Valeur', 
                                        color='Indicateur',
                                        barmode='group',
                                        title='Comparaison des indicateurs par machine KOMAX',
                                        labels={'Valeur': 'Valeur', 'Machine': 'Machine', 'Indicateur': 'Indicateur'},
                                        text=df_indicateurs_melted['Valeur'].apply(lambda x: f"{x:.2f}"))
                        fig_comparatif.update_traces(texttemplate='%{text}', textposition='outside')
                        st.plotly_chart(fig_comparatif, use_container_width=True)
                        df_all_failures = df1.groupby('Type Of Failure')['Down Time'].sum().reset_index()
            df_all_failures = df_all_failures.sort_values('Down Time', ascending=False)
            
            fig_all_failures = px.pie(df_all_failures, 
                                     values='Down Time', 
                                     names='Type Of Failure',
                                     title='Répartition des temps d\'arrêt par type de défaillance',
                                     hover_data=['Down Time'],
                                     labels={'Down Time': 'Temps d\'arrêt (heures)'})
            
            fig_all_failures.update_traces(textinfo='percent+value', 
                                         texttemplate='%{label}<br>%{value:.2f}h (%{percent})',
                                         hovertemplate='%{label}<br>Temps d\'arrêt: %{value:.2f} heures<br>Pourcentage: %{percent:.1%}')
            st.plotly_chart(fig_all_failures, use_container_width=True)
            df_pareto = df1.groupby('Type Of Failure')['Down Time'].sum().reset_index()
            df_pareto = df_pareto.sort_values(by='Down Time', ascending=False).head(3)
            df_pareto['Cumulative Percentage'] = (df_pareto['Down Time'].cumsum() / df_pareto['Down Time'].sum()) * 100

            fig_pareto = px.bar(df_pareto, x='Type Of Failure', y='Down Time', text=df_pareto['Down Time'].apply(lambda x: f"{x:.2f}"),
                                 title='Top 3 des pannes (Pareto)',
                                 labels={'Down Time': 'Temps d\'arrêt (heures)'})
            fig_pareto.update_traces(texttemplate='%{text}', textposition='outside')
            fig_pareto.add_scatter(x=df_pareto['Type Of Failure'], y=df_pareto['Cumulative Percentage'],
                                   mode='lines+markers', name='Courbe cumulative', yaxis='y2',
                                   text=df_pareto['Cumulative Percentage'].apply(lambda x: f"{x:.2f}%"))
            fig_pareto.update_layout(yaxis2=dict(title='Pourcentage cumulé', overlaying='y', side='right'))
            st.plotly_chart(fig_pareto, use_container_width=True)


            if 'Type Of Failure' in df1.columns:
                composants_specifiques = ['MARQUAGE', 'KIT-JOINT', 'MINI-APPLICATEUR']

                for composant in composants_specifiques:
                    df_composant = df1[df1['Type Of Failure'] == composant]
                    if not df_composant.empty and 'Microstop Description' in df_composant.columns:
                        df_defauts_composant = df_composant.groupby('Microstop Description')['Down Time'].sum().reset_index()
                        df_defauts_composant = df_defauts_composant.sort_values(by='Down Time', ascending=False)
                        df_defauts_composant['Cumulative Percentage'] = (df_defauts_composant['Down Time'].cumsum() / df_defauts_composant['Down Time'].sum()) * 100

                        fig_pareto_defauts_composant = px.bar(df_defauts_composant, 
                                                             x='Microstop Description', 
                                                             y='Down Time', 
                                                             text=df_defauts_composant['Down Time'].apply(lambda x: f"{x:.2f}"),
                                                             title=f'Pareto des défauts pour {composant} - {selected_week}',
                                                             labels={'Down Time': 'Temps d\'arrêt (heures)'})
                        fig_pareto_defauts_composant.update_traces(texttemplate='%{text}', textposition='outside')
                        fig_pareto_defauts_composant.add_scatter(x=df_defauts_composant['Microstop Description'], 
                                                                y=df_defauts_composant['Cumulative Percentage'],
                                                                mode='lines+markers', 
                                                                name='Courbe cumulative', 
                                                                yaxis='y2',
                                                                text=df_defauts_composant['Cumulative Percentage'].apply(lambda x: f"{x:.2f}%"))
                        fig_pareto_defauts_composant.update_layout(yaxis2=dict(title='Pourcentage cumulé', overlaying='y', side='right'))
                        st.plotly_chart(fig_pareto_defauts_composant, use_container_width=True)
                    else:
                        st.write(f"Aucune donnée disponible pour le composant : {composant}")


# Section d'analyse comparative
st.header("📈 Comparaison des Top 3 Pannes")

try:
    comparison_data = []
    for week_name, week_data in historical_data.items():
        df = week_data['df']
        if not df.empty and 'Type Of Failure' in df.columns and 'Down Time' in df.columns:
            top_pannes = df.groupby('Type Of Failure')['Down Time'].sum().nlargest(3).reset_index()
            if not top_pannes.empty:
                top_pannes['Semaine'] = week_name
                top_pannes['Rank'] = top_pannes['Down Time'].rank(ascending=False, method='dense').astype(int)
                comparison_data.append(top_pannes)
    
    if not comparison_data:
        st.error("Aucune donnée valide pour la comparaison")
        st.stop()
    
    comparison_df = pd.concat(comparison_data, ignore_index=True)
    
    plot_data = []
    for week_name in historical_data.keys():
        week_df = comparison_df[comparison_df['Semaine'] == week_name]
        for rank in range(1, 4):
            rank_df = week_df[week_df['Rank'] == rank]
            if not rank_df.empty:
                plot_data.append({
                    'Semaine': week_name,
                    'Type': rank_df.iloc[0]['Type Of Failure'],
                    'Temps': rank_df.iloc[0]['Down Time'],
                    'Rank': f"Top {rank}"
                })
    
    plot_df = pd.DataFrame(plot_data)
    
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for rank in range(1, 4):
        rank_data = plot_df[plot_df['Rank'] == f"Top {rank}"]
        if not rank_data.empty:
            fig.add_trace(go.Bar(
                x=rank_data['Semaine'],
                y=rank_data['Temps'],
                name=f'Top {rank}',
                marker_color=colors[rank-1],
                text=rank_data.apply(lambda row: f"{row['Type']}<br>{row['Temps']:.2f}h", axis=1),
                textposition='auto',
                hoverinfo='text',
                hovertext=rank_data.apply(lambda row: f"{row['Type']}<br>{row['Temps']:.2f} heures", axis=1)
            ))

    fig.update_layout(
        barmode='group',
        title=f"Comparaison des Top 3 Pannes sur {len(historical_data)} Semaines",
        xaxis_title="Semaine",
        yaxis_title="Temps d'arrêt (heures)",
        hovermode="x unified",
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erreur lors de la création du graphique: {str(e)}")
    
# Section pour l'analyse par mois
st.header("📅 Analyse par mois")

monthly_data = {}
for week_name, week_data in historical_data.items():
    df = week_data['df']
    if 'Mois' in df.columns:
        month = df['Mois'].iloc[0]
        if month not in monthly_data:
            monthly_data[month] = {'df': pd.DataFrame(), 'TO': 0}
        monthly_data[month]['df'] = pd.concat([monthly_data[month]['df'], df])
        monthly_data[month]['TO'] += week_data['TO']

if monthly_data:
    selected_month = st.selectbox("Sélectionner un mois", sorted(monthly_data.keys(), reverse=True))

    if selected_month in monthly_data:
        month_data = monthly_data[selected_month]
        df_month = month_data['df']
        TO_month = month_data['TO']
        
        with st.expander(f"Détails - {selected_month} (TO: {TO_month:.0f} heures)", expanded=True):
            if not df_month.empty and 'Type Of Failure' in df_month.columns and 'Down Time' in df_month.columns:
                df1 = df_month.dropna(how='all', axis=1).copy()
                
                if not pd.api.types.is_numeric_dtype(df1['Down Time']):
                    try:
                        df1['Down Time'] = pd.to_datetime(df1['Down Time'], format="%H:%M:%S")
                        df1['Down Time'] = df1['Down Time'].dt.hour + df1['Down Time'].dt.minute/60 + df1['Down Time'].dt.second/3600
                    except:
                        df1['Down Time'] = pd.to_numeric(df1['Down Time'], errors='coerce')
                
                TA = df1['Down Time'].sum()
                NB = df1['Down Time'].count()
                mtbf = (TO_month - TA) / NB if NB > 0 else 0
                mttr = TA / NB if NB > 0 else 0
                Di = ((TO_month - TA) / TO_month) * 100

                st.markdown("#### Indicateurs mensuels")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temps d'arrêt mensuel", f"{TA:.2f} heures")
                with col2:
                    st.metric("MTBF mensuel", f"{mtbf:.2f} heures")
                with col3:
                    st.metric("Disponibilité mensuelle", f"{Di:.1f}%")

                df_top_month = df1.groupby('Type Of Failure')['Down Time'].sum().nlargest(5).reset_index()
                fig_month = px.bar(df_top_month, 
                                 x='Type Of Failure', 
                                 y='Down Time',
                                 title=f'Top 5 pannes - {selected_month}',
                                 text='Down Time')
                
                fig_month.update_traces(
                    texttemplate='%{text:.2f}h',
                    textposition='outside',
                    marker_color='#1f77b4'
                )
                
                fig_month.update_layout(
                    xaxis_title="Type de panne",
                    yaxis_title="Temps d'arrêt (heures)",
                    xaxis=dict(tickangle=45)
                )
                
                st.plotly_chart(fig_month, use_container_width=True)
else:
    st.warning("Aucune donnée disponible pour l'analyse mensuelle")