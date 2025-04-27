from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('streamlit')
hiddenimports += [
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.web.cli'
]