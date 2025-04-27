# -*- coding: utf-8 -*-
# build.spec pour Python 3.13.2
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import sys

block_cipher = None

# ==================== CONFIGURATION DES SCRIPTS ====================
scripts = [
    'app_acc.py',  # Fichier principal
    'app_4m_folder.py',
    'app_5p_folder.py',
    'app_comp.py',
    'app_ind.py',
    'app_NB.py',
    'app_plan_action_folder.py',
    'app_TA.py',
    'app_TA_NB.py',
    'mois.py',
    'semaines.py'
]

# ==================== RESSOURCES À INCLURE ====================
data_files = [
    # Dossiers
    ('diagrammes_ishikawa/*.*', 'diagrammes_ishikawa'),
    ('monthly_data/*.*', 'monthly_data'),
    ('weekly_data/*.*', 'weekly_data'),
    ('yearly_data/*.*', 'yearly_data'),
    ('saved_reports/*.*', 'saved_reports'),
    
    # Fichiers Excel
    ('Plan d\'action coupe.xlsx', '.'),
    ('Tableaux 5p.xlsx', '.')
]

# Configuration des imports critiques pour Python 3.13
hidden_imports = [
    # Core Streamlit
    'streamlit',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.web.cli',
    
    # Gestion des métadonnées
    'importlib.metadata',
    'importlib_resources',
    'zipp',
    'typing_extensions',
    
    # Data Science
    'pandas',
    'numpy',
    'numpy.core._dtype_ctypes',
    'openpyxl',
    
    # UI
    'PIL',
    'matplotlib',
    'pyarrow'
]

a = Analysis(
    ['app_acc.py'],  # Fichier principal uniquement
    pathex=['.'],
    binaries=[],
    datas=[
        ('diagrammes_ishikawa/*', 'diagrammes_ishikawa'),
        ('*.xlsx', '.'),
        ('monthly_data/*', 'monthly_data'),
        ('weekly_data/*', 'weekly_data'),
        ('yearly_data/*', 'yearly_data')
    ],
    hiddenimports=hidden_imports,
    hookspath=['.'],
    runtime_hooks=['runtime-hook.py'],
    excludes=['Traitement des Données Excel'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, name='AppInover', debug=False, console=True, upx=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='AppInover_Files')
