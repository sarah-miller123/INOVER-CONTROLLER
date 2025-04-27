import streamlit as st
import pandas as pd
import os

def main():
    st.set_page_config(
        page_title="Plan d'Action - Komax",
        page_icon="✅",
        layout="wide"
    )

    st.title("✅ PLAN D'ACTION")
    st.markdown("📌 Suivi des actions correctives pour tous les composants Komax.")

    excel_path = "Plan d'action coupe.xlsx"

    if not os.path.exists(excel_path):
        st.error(f"❌ Fichier non trouvé : {excel_path}")
        st.info("Assurez-vous que le fichier est dans le même dossier que ce script Streamlit.")
        return

    try:
        # Lire en ignorant la 1ère ligne fusionnée
        df = pd.read_excel(excel_path, header=1)

        # Supprimer les colonnes "Unnamed"
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Remplir les cellules fusionnées verticalement
        df.fillna(method='ffill', inplace=True)

        # Supprimer les lignes dupliquées
        df = df.drop_duplicates()

        # Remplacer 1 par "100%" dans la colonne 'Etat' (ou colonnes similaires)
        for col in df.columns:
            if "Etat" in col or "Exit" in col:
                df[col] = df[col].replace(1, "100%")

        st.success("✅ Fichier chargé avec succès !")
        st.markdown(f"**Nombre total d'actions :** {len(df)}")
        st.markdown(f"**Doublons supprimés :** {len(pd.read_excel(excel_path, header=1)) - len(df)}")

        # Mettre en forme le tableau avec couleurs selon l'état
        def stylize_table(dataframe):
            def color_etat(val):
                if val == "100%":
                    return 'background-color: #a8f0a1; color: black; font-weight: bold'
                return ''
            return dataframe.style.applymap(color_etat, subset=[col for col in dataframe.columns if "Etat" in col or "Exit" in col])

        # Affichage principal sans l'index
        st.markdown("### 📋 Aperçu du plan d'action")
        st.dataframe(stylize_table(df), use_container_width=True, hide_index=True)

        # Filtres dynamiques
        with st.expander("🔍 Filtres avancés par colonne"):
            columns_to_filter = st.multiselect("Colonnes à filtrer :", df.columns)

            filtered_df = df.copy()
            for col in columns_to_filter:
                values = filtered_df[col].dropna().unique().tolist()
                selected_values = st.multiselect(f"{col} :", values, default=values)
                filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

            if columns_to_filter:
                st.markdown("### 🔎 Résultat filtré")
                st.dataframe(stylize_table(filtered_df), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.exception(e)

if __name__ == "__main__":
    main()