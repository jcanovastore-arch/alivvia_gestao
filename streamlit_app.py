import streamlit as st

st.sidebar.title("Menu")

pagina = st.sidebar.radio(
    "Navegação",
    ["Upload", "Cálculo", "Pré-OC", "OC Oficial", "Histórico", "Alocação"]
)

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
