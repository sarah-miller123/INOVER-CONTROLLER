# -*- coding: utf-8 -*-
# Importation des bibliothèques nécessaires
import streamlit as st  # Pour l'interface web
import pandas as pd  # Pour la manipulation des données
import os  # Pour les opérations sur les fichiers

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyse 5 Pourquoi",  # Titre de l'onglet du navigateur
    page_icon=":mag:",  # Icône (emoji) pour l'application
    layout="wide"  # Utilisation de toute la largeur de la page
)

# Titre principal de l'application
st.title("📊 Analyse des 5 Pourquoi par Composant")
st.markdown("---")  # Ligne de séparation

# Fonction pour charger et nettoyer les données Excel
def charger_et_nettoyer_donnees(chemin_fichier):
    """
    Charge et nettoie les données depuis un fichier Excel.
    
    Args:
        chemin_fichier (str): Chemin vers le fichier Excel
    
    Returns:
        dict: Dictionnaire contenant les DataFrames pour chaque feuille
              ou None en cas d'erreur
    """
    try:
        # Vérification de l'existence du fichier
        if not os.path.exists(chemin_fichier):
            st.error(f"Erreur : Le fichier '{chemin_fichier}' est introuvable.")
            st.info("Veuillez placer le fichier dans le même dossier que cette application.")
            return None

        # Liste des feuilles attendues dans le fichier Excel (avec les nouveaux noms)
        feuilles_attendues = ['Marquage', 'Kit-Joint', 'Mini applicateur']
        
        # Chargement du fichier Excel
        with pd.ExcelFile(chemin_fichier) as xls:
            # Vérification des feuilles disponibles
            feuilles_disponibles = xls.sheet_names
            feuilles_manquantes = [f for f in feuilles_attendues if f not in feuilles_disponibles]
            
            if feuilles_manquantes:
                st.warning(f"Attention : Feuilles manquantes - {', '.join(feuilles_manquantes)}")
            
            # Dictionnaire pour stocker les données nettoyées
            donnees_nettoyees = {}
            
            # Traitement de chaque feuille attendue
            for feuille in feuilles_attendues:
                if feuille in feuilles_disponibles:
                    # Lecture de la feuille Excel
                    df = pd.read_excel(xls, sheet_name=feuille)
                    
                    # Nettoyage des données
                    df = nettoyer_dataframe(df)
                    
                    # Stockage dans le dictionnaire
                    donnees_nettoyees[feuille] = df
                else:
                    # Création d'un DataFrame vide si la feuille est manquante
                    donnees_nettoyees[feuille] = pd.DataFrame({
                        'Erreur': [f"La feuille '{feuille}' est manquante dans le fichier"]
                    })
        
        return donnees_nettoyees
    
    except Exception as e:
        st.error(f"Une erreur s'est produite lors du chargement du fichier : {str(e)}")
        return None

# Fonction de nettoyage d'un DataFrame
def nettoyer_dataframe(df):
    """
    Nettoie un DataFrame en effectuant plusieurs opérations de standardisation.
    
    Args:
        df (pd.DataFrame): DataFrame à nettoyer
    
    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    # Suppression des lignes et colonnes complètement vides
    df = df.dropna(how='all').dropna(axis=1, how='all')
    
    # Remplissage des valeurs manquantes par des chaînes vides
    df = df.fillna('')
    
    # Standardisation des noms de colonnes
    df.columns = df.columns.str.strip().str.lower()
    
    # Suppression des espaces superflus dans les données textuelles
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Réinitialisation de l'index
    return df.reset_index(drop=True)

# Fonction pour afficher un tableau des 5 pourquoi
def afficher_5_pourquoi(df, composant):
    """
    Affiche le tableau des 5 pourquoi pour un composant donné.
    
    Args:
        df (pd.DataFrame): DataFrame contenant les données
        composant (str): Nom du composant
    """
    st.subheader(f"🔧 {composant}")
    
    # Vérification si le DataFrame contient une erreur
    if 'erreur' in df.columns:
        st.warning(df.iloc[0, 0])
        return
    
    # Affichage du tableau avec mise en forme
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={ 
            col: st.column_config.TextColumn(
                col.capitalize(),
                help=f"Colonne {col} pour l'analyse 5 pourquoi"
            ) for col in df.columns
        }
    )
    
    # Affichage des métadonnées dans un expander
    with st.expander("🔍 Détails des données"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nombre de problèmes", len(df))
        with col2:
            st.metric("Nombre de colonnes", len(df.columns))
        
        st.write("**Colonnes disponibles :**")
        st.code(", ".join(df.columns), language='text')
    
    # Affichage d'un exemple aléatoire
    if st.button(f"🎲 Exemple aléatoire - {composant}"):
        if not df.empty:
            exemple = df.sample(1).iloc[0].to_dict()
            for etape, reponse in exemple.items():
                st.markdown(f"**{etape.capitalize()}** : {reponse}")
        else:
            st.warning("Aucune donnée disponible pour cet exemple.")

# Point d'entrée principal de l'application
def main():
    # Chemin vers le fichier Excel
    FICHIER_EXCEL = "Tableaux 5p.xlsx"
    
    # Chargement des données
    donnees = charger_et_nettoyer_donnees(FICHIER_EXCEL)
    
    if donnees is not None:
        # Création des onglets pour chaque composant (avec les nouveaux noms)
        onglets = st.tabs(list(donnees.keys()))
        
        # Affichage des données dans chaque onglet
        for onglet, (composant, df) in zip(onglets, donnees.items()):
            with onglet:
                afficher_5_pourquoi(df, composant)
    
    # Pied de page
    st.markdown("---")
    st.caption("Application d'analyse des 5 pourquoi - © 2025")

# Exécution de l'application
if __name__ == "__main__":
    main()