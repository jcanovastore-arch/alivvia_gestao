import streamlit as st

from ui import upload, calculo, pre_oc, oc_oficial, historico, alocar

st.set_page_config(page_title="Alivvia Gestão", layout="wide")

# Menu lateral fixo
pagina = st.sidebar.radio(
    "Menu",
    [
        "Upload",
        "Cálculo",
        "Pré-OC",
        "OC Oficial",
        "Histórico",
        "Alocação"
    ]
)

# Roteamento das páginas
if pagina == "Upload":
    upload.app()

elif pagina == "Cálculo":
    calculo.app()

elif pagina == "Pré-OC":
    pre_oc.app()

elif pagina == "OC Oficial":
    oc_oficial.app()

elif pagina == "Histórico":
    historico.app()

elif pagina == "Alocação":
    alocar.app()
