@echo off
chcp 65001 > nul
title INOVER CONTROLLER - Lanceur Intégré v2.0
color 0B
mode con: cols=85 lines=35

:: ================================================
:: CONFIGURATION DES CHEMINS ABSOLUS
:: ================================================
set "ROOT_DIR=%~dp0"
set "STREAMLIT=%ROOT_DIR%"
set "ISHIKAWA=%ROOT_DIR%diagrammes_ishikawa\"
set "DATA_FILES=%ROOT_DIR%data\"

:: Vérification des dépendances
where python >nul 2>&1 || (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH
    echo Installez Python et vérifiez la case "Add Python to PATH"
    pause
    exit /b 1
)

where streamlit >nul 2>&1 || (
    echo [ERREUR] Streamlit n'est pas installé
    echo Installation avec: python -m pip install streamlit
    pause
    exit /b 1
)

:: ================================================
:: LANCEMENT DE L'APPLICATION PRINCIPALE
:: ================================================
cls
echo *******************************************************
echo *   I N O V E R   C O N T R O L L E R   v2.0          *
echo *******************************************************
echo.
echo Chargement de l'environnement...
timeout /t 1 >nul

echo.
echo Démarrage de l'application principale: app_acc.py
echo (Contient app_comp, app_comp2, app_ind, app_accueil)
echo (app_accueil contient 5P, 4M, Plan d'action)
echo.
timeout /t 2 >nul

if not exist "%STREAMLIT%app_acc.py" (
    echo [ERREUR] Fichier principal introuvable: app_acc.py
    pause
    exit /b 1
)

streamlit run "%STREAMLIT%app_acc.py"
pause
exit
