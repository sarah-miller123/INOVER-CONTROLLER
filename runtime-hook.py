# runtime-hook.py pour Python 3.13.2
import sys
import os
from importlib.metadata import distributions

# Correctif pour Python 3.13+
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# Patch des avertissements Streamlit
import streamlit.runtime.scriptrunner as scriptrunner
scriptrunner._thread_local = type('', (), {'__init__': lambda self: None})()

# Charge les métadonnées manquantes
for dist in distributions():
    if dist.metadata['Name'] in ('streamlit', 'pandas'):
        try:
            __import__(dist.metadata['Name'])
        except ImportError:
            pass