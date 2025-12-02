import streamlit as st
from data.storage import load_dataframe

def app():
    st.title("📦 Alocação de Estoque entre Empresas")

    st.write("Distribui o estoque entre Alivvia e JCA com base nas vendas dos últimos 60 dias.")

    # Carrega informações dos uploads
    vendas = load_dataframe("vendas_60d")
    if vendas is None:
        st.warning("Faça o upload primeiro.")
        return

    # Campo de SKU
    sku = st.text_input("SKU:")
    qtd = st.number_input("Quantidade total recebida:", min_value=1)

    if st.button("Calcular Alocação"):
        df = vendas[vendas["SKU"] == sku]

        if df.empty:
            st.error("SKU não encontrado nos uploads.")
            return

        alivvia = df.iloc[0]["Vendas_Alivvia"]
        jca = df.iloc[0]["Vendas_JCA"]
        total = alivvia + jca

        if total == 0:
            st.error("Este SKU não teve vendas no período.")
            return

        prop_alivvia = alivvia / total
        prop_jca = jca / total

        aloc_alivvia = round(qtd * prop_alivvia)
        aloc_jca = qtd - aloc_alivvia

        st.success("Alocação realizada!")
        st.metric("Alivvia", aloc_alivvia)
        st.metric("JCA", aloc_jca)
