import streamlit as st
from ui import upload, calculo, pre_oc, oc_oficial, historico

st.set_page_config(page_title="Alivvia Gestão", layout="wide")

st.sidebar.title("📦 Alivvia Gestão")
pagina = st.sidebar.radio(
    "Menu",
    ["Upload", "Cálculo", "Pré-OC", "OC Oficial", "Histórico"]
)

if pagina == "Upload":
    upload.render()
elif pagina == "Cálculo":
    calculo.render()
elif pagina == "Pré-OC":
    pre_oc.render()
elif pagina == "OC Oficial":
    oc_oficial.render()
elif pagina == "Historico":
    historico.render()
