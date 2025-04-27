import streamlit as st
import pandas as pd
import os
from unidecode import unidecode
import glob

# ==============================================
# CONFIGURATION DE L'APPLICATION
# ==============================================
st.set_page_config(
    page_title="Analyse 4M + Plan d'Action",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title("📊 Analyse des Défauts & Plans d'Action")
st.markdown("---")

# ==============================================
# FONCTIONS UTILITAIRES
# ==============================================

@st.cache_data
def charger_donnees():
    fichier = "Tableaux 5p.xlsx"
    if not os.path.exists(fichier):
        st.error("Fichier introuvable : 'Tableaux 5p.xlsx'")
        return None

    feuilles = ['Marquage', 'Kit-Joint', 'Mini applicateur']
    donnees = {}

    for feuille in feuilles:
        df = pd.read_excel(fichier, sheet_name=feuille)
        df = df.dropna(how='all').dropna(axis=1, how='all').fillna('')
        df.columns = [str(col).strip().lower() for col in df.columns]
        donnees[feuille] = df

    return donnees

def trouver_image(defaut, dossier_images):
    defaut_normalise = unidecode(defaut).lower().strip()
    fichiers_disponibles = []
    for ext in ['*.png', '*.PNG']:
        fichiers_disponibles.extend(glob.glob(os.path.join(dossier_images, ext)))

    for fichier in fichiers_disponibles:
        nom_fichier = unidecode(os.path.basename(fichier)).lower().replace('.png', '')
        nom_fichier_compare = nom_fichier.replace('_', ' ').replace('-', ' ')
        defaut_compare = defaut_normalise.replace('_', ' ').replace('-', ' ')
        if (defaut_compare == nom_fichier_compare) or (defaut_compare in nom_fichier_compare) or (nom_fichier_compare in defaut_compare):
            return fichier
    return None

@st.cache_data
def charger_plan_action():
    excel_path = "Plan d'action coupe.xlsx"
    if not os.path.exists(excel_path):
        st.warning("Fichier du plan d'action non trouvé.")
        return None
    
    # Chargement et nettoyage des données
    df = pd.read_excel(excel_path, header=1)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.fillna(method='ffill', inplace=True)
    
    # Suppression des lignes dupliquées
    df = df.drop_duplicates()
    
    # Nettoyage des colonnes et valeurs
    df.columns = [str(c).strip().lower() for c in df.columns]
    for col in df.columns:
        if "etat" in col or "exit" in col:
            df[col] = df[col].replace(1, "100%")
        # Nettoyage des valeurs de texte
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    return df

def stylize_table(dataframe):
    def color_etat(val):
        if val == "100%":
            return 'background-color: #a8f0a1; color: black; font-weight: bold'
        return ''
    return dataframe.style.applymap(color_etat, subset=[col for col in dataframe.columns if "etat" in col or "exit" in col])

# ==============================================
# APPLICATION PRINCIPALE
# ==============================================

def main():
    donnees = charger_donnees()
    plan_action_df = charger_plan_action()

    if donnees:
        composant = st.sidebar.selectbox("🧩 Sélectionnez un composant", list(donnees.keys()))
        df = donnees[composant]
        colonne_defaut = next((col for col in df.columns if 'défaut' in str(col).lower()), None)

        if colonne_defaut:
            defauts = [d for d in df[colonne_defaut].unique() if d]
            if not defauts:
                st.error("Aucun défaut trouvé.")
                return

            defaut_selectionne = st.sidebar.selectbox("🚨 Sélectionnez un défaut", defauts)

            st.subheader(f"📌 Analyse du Défaut : {defaut_selectionne}")
            st.dataframe(df[df[colonne_defaut] == defaut_selectionne], use_container_width=True)

            # ==============================================
            # Diagramme Ishikawa
            # ==============================================
            st.subheader("🔍 Diagramme 4M Ishikawa")
            dossier_images = "diagrammes_ishikawa"
            chemin_image = trouver_image(defaut_selectionne, dossier_images)

            if chemin_image:
                st.image(chemin_image, caption=f"Diagramme pour : {defaut_selectionne}", use_container_width=True)
                with open(chemin_image, "rb") as f:
                    st.download_button("📥 Télécharger le diagramme", f.read(), file_name=os.path.basename(chemin_image), mime="image/png")
            else:
                st.warning("Diagramme non trouvé.")

            # ==============================================
            # Plan d'Action Associé
            # ==============================================
            if plan_action_df is not None:
                st.subheader("📝 Plan d'Action ")
                col_defaut = next((col for col in plan_action_df.columns if 'défaut' in col), None)

                if col_defaut:
                    # Filtrage plus robuste avec nettoyage des chaînes
                    plan_filtré = plan_action_df[
                        plan_action_df[col_defaut].astype(str).str.lower().str.strip() == 
                        defaut_selectionne.lower().strip()
                    ]
                    
                    if not plan_filtré.empty:
                        st.dataframe(stylize_table(plan_filtré), use_container_width=True, hide_index=True)
                        st.markdown(f"**Nombre d'actions uniques :** {len(plan_filtré)}")
                    else:
                        st.info("Aucun plan d'action trouvé pour ce défaut.")
                else:
                    st.warning("Colonne de défaut introuvable dans le fichier plan d'action.")
        else:
            st.error("Colonne 'Défaut' introuvable dans les données.")

if __name__ == "__main__":
    main()