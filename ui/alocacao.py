import streamlit as st
import pandas as pd
from engine.calculo import get_vendas_60d  # você já tem isso no sistema

def app():

    st.title("📦 Alocação por Vendas 60d")

    st.write("Informe o SKU e a quantidade total disponível para dividir entre Alivvia e JCA.")

    sku = st.text_input("SKU")
    qtd_total = st.number_input("Quantidade total disponível", min_value=0, step=1)

    if st.button("Calcular Alocação"):

        # Obtém vendas 60d do sistema atual
        vendas = get_vendas_60d()

        if sku not in vendas.index:
            st.error("SKU não encontrado nos uploads.")
            return
        
        v_alivvia = vendas.loc[sku, "vendas_alivvia_60d"]
        v_jca = vendas.loc[sku, "vendas_jca_60d"]

        total_vendas = v_alivvia + v_jca

        if total_vendas == 0:
            st.warning("Esse SKU não teve vendas nos últimos 60 dias.")
            return

        # cálculo proporcional
        prop_alivvia = v_alivvia / total_vendas
        prop_jca = v_jca / total_vendas

        aloc_alivvia = round(qtd_total * prop_alivvia)
        aloc_jca = qtd_total - aloc_alivvia

        st.subheader("📊 Resultado da Alocação")
        st.write(f"**Alivvia:** {aloc_alivvia}")
        st.write(f"**JCA:** {aloc_jca}")
