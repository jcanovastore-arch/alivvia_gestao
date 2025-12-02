import streamlit as st
from ui.upload import app as upload_app
from ui.calculo import app as calculo_app
from ui.pre_oc import app as pre_oc_app
from ui.oc_oficial import app as oc_oficial_app
from ui.historico import app as historico_app

st.title("🚀 Alivvia Gestão — Sistema Oficial")

menu = st.sidebar.selectbox(
    "Menu",
    ["Upload", "Cálculo", "Pré-OC", "OC Oficial", "Histórico"]
)

if menu == "Upload":
    upload_app()
elif menu == "Cálculo":
    calculo_app()
elif menu == "Pré-OC":
    pre_oc_app()
elif menu == "OC Oficial":
    oc_oficial_app()
elif menu == "Histórico":
    historico_app()
