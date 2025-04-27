import pandas as pd
import plotly.express as px
import streamlit as st
import subprocess
import sys

# Interface utilisateur

# Ajouter ceci en haut de votre script
st.markdown("""
    <style>
        h1 {
            font-size: 40px !important;
            text-align: center !important;
            color: #1e88e5 !important;
            margin-bottom: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Puis votre titre normalement
if 'week' in st.session_state and st.session_state.week:
    st.title(f"Rapport de Maintenance - Semaine {st.session_state.week}")

# Ajout du bouton "Analyse des arrêts" en haut de la page
if st.button("Analyse des arrêts"):
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_accueil.py"])
        st.stop()  # Arrête l'exécution de l'app courante
    except Exception as e:
        st.error(f"Erreur lors du lancement de l'analyse: {str(e)}")

# Formulaire de saisie
with st.sidebar.form(key='form1'):
    # Sélecteur de semaine (1 à 52)
    week = st.selectbox("Numéro de semaine", options=list(range(1, 53)), index=None, placeholder="Sélectionnez la semaine")
    
    TO = st.number_input("Temps d'ouverture (heures)", value=8235)
    datafile = st.file_uploader("Importer un fichier Excel", type=['xlsx'])
    submit_button = st.form_submit_button(label='Générer le rapport')

    # Stocker la semaine dans session_state pour l'utiliser dans le titre
    if submit_button:
        st.session_state.week = week

# Traitement des données et affichage des résultats
if submit_button and datafile is not None:
    # Mettre à jour le titre avec le numéro de semaine
    st.title(f"Rapport de Maintenance - Semaine {week}")
    
    # Charger les données
    df = pd.read_excel(datafile, header=9, usecols='B:X')

    # Nettoyer les données
    df1 = df.dropna(how='all', axis=1)

    # Supprimer les lignes inutiles (PREVENTIVE MAINTENANCE et DEMARRAGE PARC)
    df1['Type Of Failure'] = df1['Type Of Failure'].str.strip()
    indexes = df1[
        (df1['Type Of Failure'] == 'DEMARRAGE PARC') | 
        (df1['Type Of Failure'] == 'PREVENTIVE MAINTENANCE')
    ].index
    df2 = df1.drop(indexes, inplace=False).copy()

    # Supprimer la dernière ligne (si elle est inutile)
    df3 = df2.drop(index=df2.index[-1], axis=0)

    # Convertir les colonnes de temps
    df3['Down Time'] = pd.to_datetime(df3['Down Time'], format="%H:%M:%S")
    df3['Delay Time'] = pd.to_datetime(df3['Delay Time'], format="%H:%M:%S")

    # Convertir les temps en heures décimales
    df3['Down Time'] = round((df3['Down Time'].dt.hour + df3['Down Time'].dt.minute/60 + df3['Down Time'].dt.second/3600), 2)
    df3['Delay Time'] = round((df3['Delay Time'].dt.hour + df3['Delay Time'].dt.minute/60 + df3['Delay Time'].dt.second/3600), 2)

    # Ajouter une nouvelle colonne 'T, I' (Temps d'intervention)
    df3.insert(loc=11, column='T, I', value=(df3['Down Time'] - df3['Delay Time']))

    # Calcul des indicateurs globaux
    TA = df3['Down Time'].sum()
    NB = df3['Down Time'].count()
    mtbf = (TO - TA) / NB
    mttr = TA / NB
    racio = (TA / TO) * 100
    Di = ((TO - TA) / TO) * 100

    # Calcul des temps d'arrêt pour le graphique en secteurs
    retart = df3['Delay Time'].sum()
    macro_arrêt = df3[df3['Down Time'] >= (10 / 60)]['Down Time'].sum()
    micro_arrêt = df3[df3['Down Time'] < (10 / 60)]['Down Time'].sum()

    # Graphique de répartition des temps d'arrêt
    df_repartition_TA = pd.DataFrame({
        'Type': ['Retart', 'Macro-arrêt', 'Micro-arrêt'],
        'Temps': [retart, macro_arrêt, micro_arrêt]
    })
    fig_pie = px.pie(df_repartition_TA, values='Temps', names='Type', title='Répartition des temps d\'arrêt')

    # --- NOUVEAU : Pareto empilé machines KOMAX par type de panne ---
    df_komax = df3[df3['Machine'].str.contains('KOMAX', na=False)]
    df_grouped = df_komax.groupby(['Machine', 'Type Of Failure'])['Down Time'].sum().reset_index()
    df_grouped = df_grouped[df_grouped['Down Time'] > 0]
    df_totals = df_grouped.groupby('Machine')['Down Time'].sum().reset_index().rename(columns={'Down Time': 'Total'})
    df_final = df_grouped.merge(df_totals, on='Machine')
    df_final = df_final.sort_values(by='Total', ascending=False)

    fig_stacked = px.bar(df_final, x='Machine', y='Down Time', color='Type Of Failure',
                         title='Temps d\'arrêt par machine KOMAX et type de panne (Pareto empilé)',
                         labels={'Down Time': 'Temps d\'arrêt (heures)', 'Machine': 'Machine'})
    st.plotly_chart(fig_stacked)


    # --- Nouveau : Graphique comparatif des indicateurs par machine KOMAX ---
    df_komax_indicateurs = df3[df3['Machine'].str.contains('KOMAX', na=False)].copy()

    # Calcul des indicateurs pour chaque machine
    df_indicateurs_komax = df_komax_indicateurs.groupby('Machine').agg({
        'Down Time': 'sum',
        'Delay Time': 'sum',
        'T, I': 'sum',
        'Type Of Failure': 'count'  # Nombre de pannes
    }).reset_index().rename(columns={'Type Of Failure': 'NB'})

    # Transformation pour le graphique à barres groupées
    df_indicateurs_melted = df_indicateurs_komax.melt(id_vars='Machine', 
                                                      value_vars=['Down Time', 'Delay Time', 'T, I', 'NB'],
                                                      var_name='Indicateur',
                                                      value_name='Valeur')

    # Affichage du graphique
    fig_comparatif = px.bar(df_indicateurs_melted, 
                            x='Machine', 
                            y='Valeur', 
                            color='Indicateur',
                            barmode='group',
                            title='Comparaison des indicateurs par machine KOMAX',
                            labels={'Valeur': 'Valeur', 'Machine': 'Machine', 'Indicateur': 'Indicateur'})

    st.plotly_chart(fig_comparatif)

    # Diagramme de Pareto des top 3 pannes
    df_pareto = df3.groupby('Type Of Failure')['Down Time'].sum().reset_index()
    df_pareto = df_pareto.sort_values(by='Down Time', ascending=False).head(3)
    df_pareto['Cumulative Percentage'] = (df_pareto['Down Time'].cumsum() / df_pareto['Down Time'].sum()) * 100

    fig_pareto = px.bar(df_pareto, x='Type Of Failure', y='Down Time', text='Down Time',
                         title='Top 3 des pannes (Pareto)')
    fig_pareto.add_scatter(x=df_pareto['Type Of Failure'], y=df_pareto['Cumulative Percentage'],
                           mode='lines+markers', name='Courbe cumulative', yaxis='y2')
    fig_pareto.update_layout(yaxis2=dict(title='Pourcentage cumulé', overlaying='y', side='right'))

    # Afficher les résultats
    st.markdown("#### Indicateurs de performance globaux ")
    st.write(f"Temps d'arrêt total (TA) : {TA:.2f} heures")
    st.write(f"MTBF : {mtbf:.2f} heures")
    st.write(f"MTTR : {mttr:.2f} heures")
    st.write(f"Racio : {racio:.2f} %")
    st.write(f"Disponibilité : {Di:.2f} %")

    st.plotly_chart(fig_pie)
    st.plotly_chart(fig_pareto)

    # Pie chart pour tous les défauts
    df_all_failures = df3.groupby('Type Of Failure')['Down Time'].sum().reset_index()
    df_all_failures = df_all_failures.sort_values('Down Time', ascending=False)
    
    fig_all_failures = px.pie(df_all_failures, 
                             values='Down Time', 
                             names='Type Of Failure',
                             title='Répartition des temps d\'arrêt par type de défaillance',
                             hover_data=['Down Time'],
                             labels={'Down Time': 'Temps d\'arrêt (heures)'})
    
    fig_all_failures.update_traces(hovertemplate='%{label}<br>Temps d\'arrêt: %{value:.2f} heures<br>Pourcentage: %{percent:.1%}')
    
    st.plotly_chart(fig_all_failures)

    # Diagrammes de Pareto pour composants spécifiques
    composants_specifiques = ['MARQUAGE', 'KIT-JOINT', 'MINI-APPLICATEUR']

    for composant in composants_specifiques:
        df_composant = df3[df3['Type Of Failure'] == composant]
        if not df_composant.empty:
            df_defauts_composant = df_composant.groupby('Microstop Description')['Down Time'].sum().reset_index()
            df_defauts_composant = df_defauts_composant.sort_values(by='Down Time', ascending=False)
            df_defauts_composant['Cumulative Percentage'] = (df_defauts_composant['Down Time'].cumsum() / df_defauts_composant['Down Time'].sum()) * 100

            fig_pareto_defauts_composant = px.bar(df_defauts_composant, x='Microstop Description', y='Down Time', text='Down Time',
                                                  title=f'Pareto des défauts pour {composant} - Semaine {week}')
            fig_pareto_defauts_composant.add_scatter(x=df_defauts_composant['Microstop Description'], y=df_defauts_composant['Cumulative Percentage'],
                                                     mode='lines+markers', name='Courbe cumulative', yaxis='y2')
            fig_pareto_defauts_composant.update_layout(yaxis2=dict(title='Pourcentage cumulé', overlaying='y', side='right'))

            st.plotly_chart(fig_pareto_defauts_composant)
        else:
            st.write(f"Aucune donnée disponible pour le composant : {composant}")

