import streamlit as st
from ui import upload, calculo, pre_oc, oc_oficial, historico, alocacao

st.set_page_config(page_title="Alivvia Gestão", layout="wide")

# --- MENU FIXO NA ESQUERDA ---
st.sidebar.title("Menu")
pagina = st.sidebar.radio(
    "Navegação",
    ["Upload", "Cálculo", "Pré-OC", "OC Oficial", "Histórico", "Alocação"],
    index=0
)

# --- ROTEAMENTO DAS PÁGINAS ---
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
    alocacao.app()
