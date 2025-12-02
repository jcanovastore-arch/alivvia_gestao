import streamlit as st
import pandas as pd

from engine.app import criar_pre_oc


st.title("📝 Pré-Ordem de Compra")

st.markdown("""
Revise, ajuste e prepare a compra antes de gerar a OC oficial.
""")


# =============================================================
# Checar dados
# =============================================================
df_pre = st.session_state.get("pre_oc", None)

if df_pre is None or len(df_pre) == 0:
    st.error("❌ Nenhum item foi enviado da página de cálculo.")
    st.stop()


st.success(f"{len(df_pre)} itens carregados para Pré-OC.")


# =============================================================
# Informações gerais
# =============================================================

st.subheader("📌 Informações da Compra")

col1, col2, col3 = st.columns(3)

with col1:
    fornecedor = st.selectbox(
        "Fornecedor",
        sorted(df_pre["Fornecedor"].dropna().unique().tolist())
    )

with col2:
    empresa = st.selectbox("Empresa", ["ALIVVIA", "JCA", "Ambas"])

with col3:
    modo = st.radio("Modo", ["Rascunho", "Gerar OC"], horizontal=True)


# =============================================================
# Tabela editável
# =============================================================

st.subheader("✏ Ajuste de Quantidades")

df_editavel = df_pre.copy()

# Converter para int
if "Compra_Sugerida" in df_editavel.columns:
    df_editavel["Compra_Sugerida"] = df_editavel["Compra_Sugerida"].fillna(0).astype(int)

df_editavel = st.data_editor(
    df_editavel,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Compra_Sugerida": st.column_config.NumberColumn(
            "Quantidade",
            min_value=0,
            step=1,
            format="%d",
        )
    }
)

st.session_state["df_pre_editado"] = df_editavel


# =============================================================
# Adicionar SKU manualmente
# =============================================================

st.markdown("---")
st.subheader("➕ Adicionar SKU manualmente")

col_a1, col_a2, col_a3 = st.columns([2,1,1])

with col_a1:
    sku_manual = st.text_input("SKU")

with col_a2:
    qtd_manual = st.number_input("Quantidade", min_value=1, value=1)

with col_a3:
    if st.button("Adicionar"):
        if sku_manual.strip() == "":
            st.error("SKU inválido.")
        else:
            nova_linha = {
                "SKU": sku_manual.upper(),
                "Empresa": empresa,
                "Fornecedor": fornecedor,
                "Compra_Sugerida": int(qtd_manual),
                "Preco_Custo": 0,
                "Valor_Total_R$": 0
            }

            df_editavel = pd.concat([df_editavel, pd.DataFrame([nova_linha])], ignore_index=True)
            st.session_state["df_pre_editado"] = df_editavel
            st.success(f"SKU {sku_manual.upper()} adicionado.")


# =============================================================
# Botões finais
# =============================================================

st.markdown("---")

col_b1, col_b2 = st.columns(2)

with col_b1:
    if st.button("💾 Salvar Como Rascunho"):
        st.session_state["rascunho"] = df_editavel
        st.success("✔ Pré-OC salva como rascunho!")

with col_b2:
    if st.button("📦 Gerar OC"):
        st.session_state["oc_base"] = {
            "fornecedor": fornecedor,
            "empresa": empresa,
            "df": df_editavel
        }
        st.success("✔ OC preparada! Finalize na página 'OC Oficial'.")
