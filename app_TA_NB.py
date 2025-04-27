import pandas as pd
import plotly.express as px
import streamlit as st
import subprocess
import sys
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(layout="wide", page_title="Rapport de Maintenance")

# Style CSS personnalisé
st.markdown("""
    <style>
        h1 {
            font-size: 40px !important;
            text-align: center !important;
            color: #1e88e5 !important;
            margin-bottom: 20px !important;
        }
        h2 {
            border-bottom: 2px solid #1e88e5;
            padding-bottom: 5px;
            margin-top: 40px !important;
        }
        h3 {
            margin-top: 25px !important;
            color: #2e7d32 !important;
        }
        .metric-box {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .pareto-section {
            background-color: #f9f9f9;
            border-left: 4px solid #1e88e5;
            padding: 15px;
            margin: 25px 0;
            border-radius: 0 8px 8px 0;
        }
        .stButton>button {
            background-color: #1e88e5;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Titre principal
if 'week' in st.session_state and st.session_state.week:
    st.title(f"📊 Rapport de Maintenance - Semaine {st.session_state.week}")

# Bouton "Analyse des arrêts"
if st.button("🔍 Analyse des arrêts"):
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_accueil.py"])
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors du lancement de l'analyse: {str(e)}")

# Formulaire de saisie
with st.sidebar.form(key='form1'):
    st.markdown("### Paramètres d'analyse")
    week = st.selectbox("Numéro de semaine", options=list(range(1, 53)), index=None, placeholder="Sélectionnez la semaine")
    TO = st.number_input("Temps d'ouverture (heures)", min_value=1, value=168)
    datafile = st.file_uploader("Importer le fichier Excel", type=['xlsx'], accept_multiple_files=False)
    submit_button = st.form_submit_button(label='🚀 Générer le rapport')
    
    if submit_button:
        st.session_state.week = week
        st.session_state.TO = TO

# Traitement des données
if submit_button and datafile is not None:
    try:
        # Chargement des données
        df = pd.read_excel(datafile, header=9, usecols='B:X')
        
        # Nettoyage des données
        df1 = df.dropna(how='all', axis=1)
        df1['Type Of Failure'] = df1['Type Of Failure'].str.strip()
        
        # Suppression des lignes non pertinentes
        indexes = df1[
            (df1['Type Of Failure'] == 'DEMARRAGE PARC') | 
            (df1['Type Of Failure'] == 'PREVENTIVE MAINTENANCE')
        ].index
        df2 = df1.drop(indexes, inplace=False).copy()
        df3 = df2.drop(index=df2.index[-1], axis=0)
        
        # Conversion des temps
        df3['Down Time'] = pd.to_datetime(df3['Down Time'], format="%H:%M:%S")
        df3['Delay Time'] = pd.to_datetime(df3['Delay Time'], format="%H:%M:%S")
        df3['Down Time'] = round((df3['Down Time'].dt.hour + df3['Down Time'].dt.minute/60 + df3['Down Time'].dt.second/3600), 2)
        df3['Delay Time'] = round((df3['Delay Time'].dt.hour + df3['Delay Time'].dt.minute/60 + df3['Delay Time'].dt.second/3600), 2)
        df3.insert(loc=11, column='T, I', value=(df3['Down Time'] - df3['Delay Time']))

        # Calcul des indicateurs globaux
        TA = df3['Down Time'].sum()
        NB = df3['Down Time'].count()
        mtbf = (TO - TA) / NB if NB > 0 else 0
        mttr = TA / NB if NB > 0 else 0
        racio = (TA / TO) * 100 if TO > 0 else 0
        Di = ((TO - TA) / TO) * 100 if TO > 0 else 0

        # =============================================
        # SECTION 1: Indicateurs globaux
        # =============================================
        st.markdown("## 📈 Indicateurs globaux")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-box">
                    <h3>Temps d'arrêt (TA)</h3>
                    <p style="font-size:24px; text-align:center; color:#d32f2f;">{TA:.1f} h</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-box">
                    <h3>Nombre d'arrêts (NB)</h3>
                    <p style="font-size:24px; text-align:center; color:#1976d2;">{NB}</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-box">
                    <h3>Disponibilité</h3>
                    <p style="font-size:24px; text-align:center; color:#388e3c;">{Di:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                <div class="metric-box">
                    <h3>MTBF / MTTR</h3>
                    <p style="font-size:24px; text-align:center; color:#7b1fa2;">{mtbf:.1f}h / {mttr:.1f}h</p>
                </div>
            """, unsafe_allow_html=True)

        # =============================================
        # SECTION 2: Analyses KOMAX séparées
        # =============================================
        df_komax = df3[df3['Machine'].str.contains('KOMAX', na=False, case=False)]
        
        if not df_komax.empty:
            st.markdown("---")
            st.markdown("## 🏭 Analyse par machine KOMAX")
            
            # 1. Comparaison des indicateurs par machine KOMAX
            st.markdown("### 🔄 Comparaison des indicateurs par machine")
            df_komax_metrics = df_komax.groupby('Machine').agg({
                'Down Time': ['sum', 'count'],
                'Delay Time': 'sum',
                'T, I': 'sum'
            }).reset_index()
            
            df_komax_metrics.columns = ['Machine', 'Temps arrêt', 'Nb arrêts', 'Temps retard', 'Temps intervention']
            
            fig_metrics = go.Figure()
            fig_metrics.add_trace(go.Bar(
                x=df_komax_metrics['Machine'],
                y=df_komax_metrics['Temps arrêt'],
                name='Temps arrêt (h)',
                marker_color='#FFA15A'
            ))
            fig_metrics.add_trace(go.Bar(
                x=df_komax_metrics['Machine'],
                y=df_komax_metrics['Nb arrêts'],
                name='Nombre arrêts',
                marker_color='#00CC96'
            ))
            fig_metrics.add_trace(go.Bar(
                x=df_komax_metrics['Machine'],
                y=df_komax_metrics['Temps intervention'],
                name='Temps intervention (h)',
                marker_color='#AB63FA'
            ))
            
            fig_metrics.update_layout(
                barmode='group',
                height=500,
                title="Comparaison des indicateurs par machine KOMAX",
                xaxis_title="Machine",
                yaxis_title="Valeur",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_metrics, use_container_width=True)
            
            # 2. Temps d'arrêt par machine KOMAX (séparé)
            st.markdown("### ⏱ Temps d'arrêt par machine KOMAX")
            df_komax_ta = df_komax.groupby('Machine')['Down Time'].sum().reset_index().sort_values('Down Time', ascending=False)
            
            fig_ta = px.bar(
                df_komax_ta,
                x='Machine',
                y='Down Time',
                text='Down Time',
                color='Down Time',
                color_continuous_scale='Bluered',
                title="Temps d'arrêt total par machine (heures)"
            )
            fig_ta.update_traces(texttemplate='%{y:.1f}h', textposition='outside')
            fig_ta.update_layout(yaxis_title="Temps d'arrêt (heures)")
            st.plotly_chart(fig_ta, use_container_width=True)
            
            # 3. Nombre d'arrêts par machine KOMAX (séparé)
            st.markdown("### 🔢 Nombre d'arrêts par machine KOMAX")
            df_komax_nb = df_komax.groupby('Machine').size().reset_index(name='Count').sort_values('Count', ascending=False)
            
            fig_nb = px.bar(
                df_komax_nb,
                x='Machine',
                y='Count',
                text='Count',
                color='Count',
                color_continuous_scale='Teal',
                title="Nombre d'arrêts par machine"
            )
            fig_nb.update_traces(textposition='outside')
            fig_nb.update_layout(yaxis_title="Nombre d'arrêts")
            st.plotly_chart(fig_nb, use_container_width=True)
            
            # 4. Répartition des temps d'arrêt par type de défaillance KOMAX
            st.markdown("### 🥧 Répartition des temps d'arrêt (KOMAX)")
            df_komax_ta_type = df_komax.groupby('Type Of Failure')['Down Time'].sum().reset_index()
            
            fig_ta_type = px.pie(
                df_komax_ta_type,
                values='Down Time',
                names='Type Of Failure',
                title="Temps d'arrêt par type de défaillance",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_ta_type.update_traces(
                textinfo='percent+value', 
                texttemplate='%{label}<br>%{value:.1f}h (%{percent})',
                pull=[0.1 if i == 0 else 0 for i in range(len(df_komax_ta_type))]
            )
            st.plotly_chart(fig_ta_type, use_container_width=True)
            
            # 5. Répartition du nombre d'arrêts par type de défaillance KOMAX
            st.markdown("### 🍰 Répartition du nombre d'arrêts (KOMAX)")
            df_komax_nb_type = df_komax.groupby('Type Of Failure').size().reset_index(name='Count')
            
            fig_nb_type = px.pie(
                df_komax_nb_type,
                values='Count',
                names='Type Of Failure',
                title="Nombre d'arrêts par type de défaillance",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Emrld
            )
            fig_nb_type.update_traces(
                textinfo='percent+value', 
                texttemplate='%{label}<br>%{value} (%{percent})',
                pull=[0.1 if i == 0 else 0 for i in range(len(df_komax_nb_type))]
            )
            st.plotly_chart(fig_nb_type, use_container_width=True)

            # =============================================
            # SECTION 3: Pareto combinés KOMAX
            # =============================================
            st.markdown("---")
            st.markdown('<div class="pareto-section"><h2>📊 Pareto combinés NB/TA - Machines KOMAX</h2></div>', unsafe_allow_html=True)
            
            # 1. Pareto combiné par machine KOMAX
            st.markdown("#### 📌 Machines KOMAX")
            df_komax_combined = df_komax.groupby('Machine').agg(
                NB=('Down Time', 'count'),
                TA=('Down Time', 'sum')
            ).reset_index().sort_values('TA', ascending=False)
            
            fig_komax_combined = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Barres NB
            fig_komax_combined.add_trace(
                go.Bar(
                    x=df_komax_combined['Machine'],
                    y=df_komax_combined['NB'],
                    name="Nombre d'arrêts",
                    marker_color='#1f77b4',
                    text=df_komax_combined['NB'],
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            # Barres TA
            fig_komax_combined.add_trace(
                go.Bar(
                    x=df_komax_combined['Machine'],
                    y=df_komax_combined['TA'],
                    name="Temps d'arrêt (h)",
                    marker_color='#ff7f0e',
                    text=df_komax_combined['TA'].round(1),
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            # Courbes cumulatives
            df_komax_combined['Cumul_NB'] = (df_komax_combined['NB'].cumsum()/df_komax_combined['NB'].sum())*100
            df_komax_combined['Cumul_TA'] = (df_komax_combined['TA'].cumsum()/df_komax_combined['TA'].sum())*100
            
            fig_komax_combined.add_trace(
                go.Scatter(
                    x=df_komax_combined['Machine'],
                    y=df_komax_combined['Cumul_NB'],
                    name="% Cumul NB",
                    line=dict(color='#1f77b4', dash='dot'),
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            fig_komax_combined.add_trace(
                go.Scatter(
                    x=df_komax_combined['Machine'],
                    y=df_komax_combined['Cumul_TA'],
                    name="% Cumul TA",
                    line=dict(color='#ff7f0e', dash='dot'),
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            fig_komax_combined.update_layout(
                title="Comparaison NB/TA par machine KOMAX",
                yaxis_title="Nombre/Temps d'arrêt",
                yaxis2_title="Pourcentage cumulé",
                barmode='group',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_komax_combined, use_container_width=True)
            
            # 2. Pareto combiné par type de panne KOMAX
            st.markdown("#### 📌 Types de panne KOMAX")
            df_komax_type_combined = df_komax.groupby('Type Of Failure').agg(
                NB=('Down Time', 'count'),
                TA=('Down Time', 'sum')
            ).reset_index().sort_values('TA', ascending=False).head(8)
            
            fig_komax_type_combined = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_komax_type_combined.add_trace(
                go.Bar(
                    x=df_komax_type_combined['Type Of Failure'],
                    y=df_komax_type_combined['NB'],
                    name="Nombre d'arrêts",
                    marker_color='#1f77b4',
                    text=df_komax_type_combined['NB'],
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            fig_komax_type_combined.add_trace(
                go.Bar(
                    x=df_komax_type_combined['Type Of Failure'],
                    y=df_komax_type_combined['TA'],
                    name="Temps d'arrêt (h)",
                    marker_color='#ff7f0e',
                    text=df_komax_type_combined['TA'].round(1),
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            df_komax_type_combined['Cumul_NB'] = (df_komax_type_combined['NB'].cumsum()/df_komax_type_combined['NB'].sum())*100
            df_komax_type_combined['Cumul_TA'] = (df_komax_type_combined['TA'].cumsum()/df_komax_type_combined['TA'].sum())*100
            
            fig_komax_type_combined.add_trace(
                go.Scatter(
                    x=df_komax_type_combined['Type Of Failure'],
                    y=df_komax_type_combined['Cumul_NB'],
                    name="% Cumul NB",
                    line=dict(color='#1f77b4', dash='dot'),
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            fig_komax_type_combined.add_trace(
                go.Scatter(
                    x=df_komax_type_combined['Type Of Failure'],
                    y=df_komax_type_combined['Cumul_TA'],
                    name="% Cumul TA",
                    line=dict(color='#ff7f0e', dash='dot'),
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            fig_komax_type_combined.update_layout(
                title="Comparaison NB/TA par type de panne KOMAX (Top 8)",
                yaxis_title="Nombre/Temps d'arrêt",
                yaxis2_title="Pourcentage cumulé",
                barmode='group',
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_komax_type_combined, use_container_width=True)

        # =============================================
        # SECTION 4: Analyses globales séparées
        # =============================================
        st.markdown("---")
        st.markdown("## 🌍 Analyse globale")
        
        # 1. Temps d'arrêt par type de panne (global)
        st.markdown("### ⏱ Top 10 - Temps d'arrêt par type de panne")
        df_ta_global = df3.groupby('Type Of Failure')['Down Time'].sum().reset_index().sort_values('Down Time', ascending=False).head(10)
        
        fig_ta_global = px.bar(
            df_ta_global,
            x='Type Of Failure',
            y='Down Time',
            text='Down Time',
            color='Down Time',
            color_continuous_scale='Viridis',
            title="Top 10 des types de panne par temps d'arrêt"
        )
        fig_ta_global.update_traces(texttemplate='%{y:.1f}h', textposition='outside')
        fig_ta_global.update_layout(yaxis_title="Temps d'arrêt (heures)", xaxis_tickangle=-45)
        st.plotly_chart(fig_ta_global, use_container_width=True)
        
        # 2. Nombre d'arrêts par type de panne (global)
        st.markdown("### 🔢 Top 10 - Nombre d'arrêts par type de panne")
        df_nb_global = df3.groupby('Type Of Failure').size().reset_index(name='Count').sort_values('Count', ascending=False).head(10)
        
        fig_nb_global = px.bar(
            df_nb_global,
            x='Type Of Failure',
            y='Count',
            text='Count',
            color='Count',
            color_continuous_scale='Purp',
            title="Top 10 des types de panne par nombre d'occurrences"
        )
        fig_nb_global.update_traces(textposition='outside')
        fig_nb_global.update_layout(yaxis_title="Nombre d'arrêts", xaxis_tickangle=-45)
        st.plotly_chart(fig_nb_global, use_container_width=True)
        
        # 3. Répartition globale des temps d'arrêt
        st.markdown("### 🥧 Répartition des temps d'arrêt (Global)")
        df_ta_pie = df3.groupby('Type Of Failure')['Down Time'].sum().reset_index()
        
        fig_ta_pie = px.pie(
            df_ta_pie,
            values='Down Time',
            names='Type Of Failure',
            title="Répartition des temps d'arrêt par type de panne",
            hole=0.3
        )
        fig_ta_pie.update_traces(
            textinfo='percent+value', 
            texttemplate='%{label}<br>%{value:.1f}h (%{percent})',
            pull=[0.1 if i == 0 else 0 for i in range(len(df_ta_pie))]
        )
        st.plotly_chart(fig_ta_pie, use_container_width=True)
        
        # 4. Répartition globale du nombre d'arrêts
        st.markdown("### 🍰 Répartition du nombre d'arrêts (Global)")
        df_nb_pie = df3.groupby('Type Of Failure').size().reset_index(name='Count')
        
        fig_nb_pie = px.pie(
            df_nb_pie,
            values='Count',
            names='Type Of Failure',
            title="Répartition du nombre d'arrêts par type de panne",
            hole=0.3
        )
        fig_nb_pie.update_traces(
            textinfo='percent+value', 
            texttemplate='%{label}<br>%{value} (%{percent})',
            pull=[0.1 if i == 0 else 0 for i in range(len(df_nb_pie))]
        )
        st.plotly_chart(fig_nb_pie, use_container_width=True)

        # =============================================
        # SECTION 5: Pareto combinés globaux
        # =============================================
        st.markdown("---")
        st.markdown('<div class="pareto-section"><h2>📊 Pareto combinés NB/TA - Global</h2></div>', unsafe_allow_html=True)
        
        # 1. Pareto combiné global par type de panne
        st.markdown("#### 🌐 Types de panne (Top 8)")
        df_global_combined = df3.groupby('Type Of Failure').agg(
            NB=('Down Time', 'count'),
            TA=('Down Time', 'sum')
        ).reset_index().sort_values('TA', ascending=False).head(8)
        
        fig_global_combined = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_global_combined.add_trace(
            go.Bar(
                x=df_global_combined['Type Of Failure'],
                y=df_global_combined['NB'],
                name="Nombre d'arrêts",
                marker_color='#1f77b4',
                text=df_global_combined['NB'],
                textposition='outside'
            ),
            secondary_y=False
        )
        
        fig_global_combined.add_trace(
            go.Bar(
                x=df_global_combined['Type Of Failure'],
                y=df_global_combined['TA'],
                name="Temps d'arrêt (h)",
                marker_color='#ff7f0e',
                text=df_global_combined['TA'].round(1),
                textposition='outside'
            ),
            secondary_y=False
        )
        
        df_global_combined['Cumul_NB'] = (df_global_combined['NB'].cumsum()/df_global_combined['NB'].sum())*100
        df_global_combined['Cumul_TA'] = (df_global_combined['TA'].cumsum()/df_global_combined['TA'].sum())*100
        
        fig_global_combined.add_trace(
            go.Scatter(
                x=df_global_combined['Type Of Failure'],
                y=df_global_combined['Cumul_NB'],
                name="% Cumul NB",
                line=dict(color='#1f77b4', dash='dot'),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig_global_combined.add_trace(
            go.Scatter(
                x=df_global_combined['Type Of Failure'],
                y=df_global_combined['Cumul_TA'],
                name="% Cumul TA",
                line=dict(color='#ff7f0e', dash='dot'),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig_global_combined.update_layout(
            title="Comparaison NB/TA par type de panne (Top 8)",
            yaxis_title="Nombre/Temps d'arrêt",
            yaxis2_title="Pourcentage cumulé",
            barmode='group',
            height=500,
            xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_global_combined, use_container_width=True)
        
        # 2. Pareto combiné pour composants spécifiques
        st.markdown("#### ⚙️ Composants spécifiques")
        composants = ['MARQUAGE', 'KIT-JOINT', 'MINI-APPLICATEUR']
        
        for composant in composants:
            df_comp = df3[df3['Type Of Failure'] == composant]
            if not df_comp.empty:
                st.markdown(f"**{composant}**")
                df_comp_combined = df_comp.groupby('Microstop Description').agg(
                    NB=('Down Time', 'count'),
                    TA=('Down Time', 'sum')
                ).reset_index().sort_values('TA', ascending=False).head(5)
                
                if len(df_comp_combined) > 0:
                    fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    fig_comp.add_trace(
                        go.Bar(
                            x=df_comp_combined['Microstop Description'],
                            y=df_comp_combined['NB'],
                            name="Nombre d'arrêts",
                            marker_color='#1f77b4',
                            text=df_comp_combined['NB'],
                            textposition='outside'
                        ),
                        secondary_y=False
                    )
                    
                    fig_comp.add_trace(
                        go.Bar(
                            x=df_comp_combined['Microstop Description'],
                            y=df_comp_combined['TA'],
                            name="Temps d'arrêt (h)",
                            marker_color='#ff7f0e',
                            text=df_comp_combined['TA'].round(1),
                            textposition='outside'
                        ),
                        secondary_y=False
                    )
                    
                    df_comp_combined['Cumul_NB'] = (df_comp_combined['NB'].cumsum()/df_comp_combined['NB'].sum())*100
                    df_comp_combined['Cumul_TA'] = (df_comp_combined['TA'].cumsum()/df_comp_combined['TA'].sum())*100
                    
                    fig_comp.add_trace(
                        go.Scatter(
                            x=df_comp_combined['Microstop Description'],
                            y=df_comp_combined['Cumul_NB'],
                            name="% Cumul NB",
                            line=dict(color='#1f77b4', dash='dot'),
                            mode='lines+markers'
                        ),
                        secondary_y=True
                    )
                    
                    fig_comp.add_trace(
                        go.Scatter(
                            x=df_comp_combined['Microstop Description'],
                            y=df_comp_combined['Cumul_TA'],
                            name="% Cumul TA",
                            line=dict(color='#ff7f0e', dash='dot'),
                            mode='lines+markers'
                        ),
                        secondary_y=True
                    )
                    
                    fig_comp.update_layout(
                        title=f"Comparaison NB/TA pour {composant}",
                        yaxis_title="Nombre/Temps d'arrêt",
                        yaxis2_title="Pourcentage cumulé",
                        barmode='group',
                        height=400,
                        xaxis_tickangle=-45,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.warning(f"Aucune donnée valide pour le composant {composant}")
            else:
                st.warning(f"Aucune donnée disponible pour le composant {composant}")

    except Exception as e:
        st.error(f"Une erreur est survenue lors du traitement des données: {str(e)}")