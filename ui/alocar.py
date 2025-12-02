import streamlit as st
import pandas as pd
from data.cache import get_cache

def app():
    st.title("🔀 Alocação entre Empresas")

    # Aviso inicial
    st.info("Use esta aba para dividir uma quantidade entre ALIVVIA e JCA automaticamente, "
            "baseado nas vendas dos últimos 60 dias (simples + kits).")

    cache = get_cache()

    # Verificação se os cálculos já estão prontos
    if "vendas_ali" not in cache or "vendas_jca" not in cache:
        st.warning("⚠️ Primeiro gere os cálculos na aba 'Cálculo'.")
        return

    vendas_ali = cache["vendas_ali"]
    vendas_jca = cache["vendas_jca"]

    # Entrada do usuário
    sku = st.text_input("SKU")
    quantidade_total = st.number_input("Quantidade total a alocar", min_value=1, step=1)

    if st.button("Calcular Alocação"):
        if sku not in vendas_ali.index or sku not in vendas_jca.index:
            st.error("SKU não encontrado nas vendas consolidadas.")
            return

        v_ali = vendas_ali.loc[sku]
        v_jca = vendas_jca.loc[sku]

        total_vendas = v_ali + v_jca

        if total_vendas == 0:
            st.error("Este SKU não teve vendas nos últimos 60 dias.")
            return

        # Regra simples: divide proporcionalmente às vendas
        proporcao_ali = v_ali / total_vendas
        proporcao_jca = v_jca / total_vendas

        qtd_ali = round(quantidade_total * proporcao_ali)
        qtd_jca = quantidade_total - qtd_ali  # garante 100%

        resultado = pd.DataFrame({
            "SKU": [sku, sku],
            "Empresa": ["ALIVVIA", "JCA"],
            "Vendas 60d": [v_ali, v_jca],
            "Proporção": [proporcao_ali, proporcao_jca],
            "Quantidade Alocada": [qtd_ali, qtd_jca]
        })

        st.success("Alocação concluída com sucesso.")
        st.table(resultado)
