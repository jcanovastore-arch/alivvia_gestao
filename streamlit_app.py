import streamlit as st

from ui import upload, calculo, pre_oc, oc_oficial, historico, alocacao

st.set_page_config(page_title="Alivvia Gestão", layout="wide")

MENU = {
    "Upload": upload,
    "Cálculo": calculo,
    "Pré-OC": pre_oc,
    "OC Oficial": oc_oficial,
    "Histórico": historico,
    "Alocação": alocacao
}

st.sidebar.title("Menu")
escolha = st.sidebar.selectbox(" ", list(MENU.keys()))

MENU[escolha].app()
