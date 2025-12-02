import streamlit as st
import pandas as pd

from engine.app import executar_calculo


st.title("📊 Cálculo Consolidado — Reposição & Compras")

st.markdown("""
Ajuste os parâmetros, aplique filtros e envie o resultado para a Pré-OC.
""")


# =============================================================
# Verificar se upload está completo
# =============================================================
u = st.session_state.get("uploads", None)

if u is None or u["padrao"] is None:
    st.error("❌ Você precisa carregar o Padrão antes.")
    st.stop()

if not all(u["alivvia"].values()) or not all(u["jca"].values()):
    st.error("❌ Suba todos os arquivos de ALIVVIA e JCA antes de continuar.")
    st.stop()


# =============================================================
# Parâmetros de cálculo
# =============================================================
st.subheader("⚙ Parâmetros do Cálculo")

col1, col2, col3 = st.columns(3)

with col1:
    horizonte = st.number_input("Horizonte (dias)", 1, 180, 60)

with col2:
    lead_time = st.number_input("Lead Time (dias)", 0, 60, 20)

with col3:
    crescimento = st.number_input("Crescimento (%)", -50, 200, 0)


# =============================================================
# Rodar cálculo em botão
# =============================================================
if st.button("🔄 Executar Cálculo"):
    st.info("Processando...")

    # ALIVVIA
    df_full_a = u["alivvia"]["full"]
    df_vendas_a = u["alivvia"]["vendas"]
    df_fisico_a = u["alivvia"]["fisico"]

    # JCA
    df_full_j = u["jca"]["full"]
    df_vendas_j = u["jca"]["vendas"]
    df_fisico_j = u["jca"]["fisico"]

    # Padrão
    df_kits = u["padrao"]

    # Carregar dataframes
    df_full_a = pd.read_excel(df_full_a)
    df_vendas_a = pd.read_excel(df_vendas_a)
    df_fisico_a = pd.read_excel(df_fisico_a)

    df_full_j = pd.read_excel(df_full_j)
    df_vendas_j = pd.read_excel(df_vendas_j)
    df_fisico_j = pd.read_excel(df_fisico_j)

    # Rodar cálculo
    df_calculo_a = executar_calculo(df_full_a, df_fisico_a, df_vendas_a, df_kits,
                                    horizonte, lead_time, crescimento)
    df_calculo_a["Empresa"] = "ALIVVIA"

    df_calculo_j = executar_calculo(df_full_j, df_fisico_j, df_vendas_j, df_kits,
                                    horizonte, lead_time, crescimento)
    df_calculo_j["Empresa"] = "JCA"

    # Unir tudo
    df_final = pd.concat([df_calculo_a, df_calculo_j], ignore_index=True)

    st.session_state["df_calculo"] = df_final
    st.success("✔ Cálculo concluído! Aplique filtros abaixo.")


# =============================================================
# Filtragem (quando cálculo estiver pronto)
# =============================================================

df = st.session_state.get("df_calculo", None)

if df is None:
    st.stop()

st.subheader("🔍 Filtros")

colf1, colf2, colf3 = st.columns(3)

with colf1:
    fornecedores = sorted(df["Fornecedor"].dropna().unique().tolist())
    fornecedor_sel = st.selectbox("Fornecedor", ["Todos"] + fornecedores)

with colf2:
    empresa_sel = st.selectbox("Empresa", ["Todas", "ALIVVIA", "JCA"])

with colf3:
    sku_query = st.text_input("Buscar SKU / palavra")

# Aplicar filtros
df_filtrado = df.copy()

if fornecedor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Fornecedor"] == fornecedor_sel]

if empresa_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Empresa"] == empresa_sel]

if sku_query:
    df_filtrado = df_filtrado[df_filtrado["SKU"].str.contains(sku_query.upper(), na=False)]

st.markdown("### 📋 Resultado")

st.dataframe(df_filtrado, height=500, use_container_width=True)


# =============================================================
# Botão para enviar à Pré-OC
# =============================================================
st.markdown("---")

if st.button("➡ Enviar para Pré-OC"):
    st.session_state["pre_oc"] = df_filtrado
    st.success("✔ Enviado para Pré-OC! Acesse a página 'Pré-OC' no menu.")
