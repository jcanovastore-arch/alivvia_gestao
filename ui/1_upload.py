import streamlit as st
import pandas as pd
from pathlib import Path

from engine.normalizador import normalize_cols
from engine.app import carregar_arquivos

st.title("📤 Uploads & Catálogo — ALIVVIA Gestão")

st.markdown("""
Suba aqui todos os arquivos necessários para o cálculo de reposição.
""")

# =============================================================
# Session State inicial
# =============================================================

if "uploads" not in st.session_state:
    st.session_state.uploads = {
        "alivvia": {"full": None, "vendas": None, "fisico": None},
        "jca": {"full": None, "vendas": None, "fisico": None},
        "padrao": None,
    }

# =============================================================
# Bloco de Carregar Padrão (Google Sheets)
# =============================================================

st.header("📘 Carregar Padrão (Catálogo + Kits)")

PADRAO_URL = "https://docs.google.com/spreadsheets/d/1RXXXXXX/export?format=xlsx"  # COLOCAR LINK REAL AQUI

col_p1, col_p2 = st.columns([2,1])

with col_p1:
    st.text_input("Link do Google Sheets:", PADRAO_URL, key="padrao_link")

with col_p2:
    if st.button("Carregar Padrão"):
        try:
            df_p = pd.read_excel(st.session_state.padrao_link)
            st.session_state.uploads["padrao"] = df_p
            st.success("✔ Padrão carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar padrão: {e}")

if st.session_state.uploads["padrao"] is not None:
    st.success("Catálogo/Kits carregado.")

# =============================================================
# UPLOADS DAS EMPRESAS
# =============================================================

st.header("🏢 Uploads das Empresas")


def bloco_empresa(nome_empresa):
    st.subheader(f"📦 {nome_empresa.upper()}")

    full = st.file_uploader(f"FULL — {nome_empresa.upper()}", type=["xlsx", "csv"])
    vendas = st.file_uploader(f"Vendas 60 dias — {nome_empresa.upper()}", type=["xlsx", "csv"])
    fisico = st.file_uploader(f"Estoque Físico — {nome_empresa.upper()}", type=["xlsx", "csv"])

    if full:
        st.session_state.uploads[nome_empresa]["full"] = full
        st.success("FULL carregado.")

    if vendas:
        st.session_state.uploads[nome_empresa]["vendas"] = vendas
        st.success("Vendas carregado.")

    if fisico:
        st.session_state.uploads[nome_empresa]["fisico"] = fisico
        st.success("Estoque físico carregado.")

    # Botão limpar
    if st.button(f"Limpar arquivos {nome_empresa.upper()}"):
        st.session_state.uploads[nome_empresa] = {"full": None, "vendas": None, "fisico": None}
        st.warning(f"{nome_empresa.upper()} limpo!")


col1, col2 = st.columns(2)
with col1:
    bloco_empresa("alivvia")

with col2:
    bloco_empresa("jca")

# =============================================================
# STATUS FINAL
# =============================================================

st.markdown("---")
st.subheader("📌 Status dos Uploads")

ok_padrao = st.session_state.uploads["padrao"] is not None
ok_alivvia = all(st.session_state.uploads["alivvia"].values())
ok_jca = all(st.session_state.uploads["jca"].values())

st.write(f"📘 Padrão: {'✔' if ok_padrao else '❌'}")
st.write(f"🏢 ALIVVIA: {'✔' if ok_alivvia else '❌'}")
st.write(f"🏢 JCA: {'✔' if ok_jca else '❌'}")

if ok_padrao and ok_alivvia and ok_jca:
    st.success("✔ Tudo pronto! Vá para a página **Cálculo** no menu.")
else:
    st.info("⏳ Aguarde até todos os arquivos serem enviados.")
