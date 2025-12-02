import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# ====== INICIALIZAÇÃO SUPABASE ======
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def carregar_ocs():
    """Retorna DataFrame com todas as OCs"""
    res = supabase.table("ocs").select("*").order("criado_em", desc=True).execute()
    return pd.DataFrame(res.data)

def carregar_itens(oc_id):
    """Carrega itens da OC específica"""
    res = supabase.table("ocs_itens").select("*").eq("oc_id", oc_id).execute()
    return pd.DataFrame(res.data)

def marcar_recebido(oc_id, item_id, qtd_recebida):
    """Atualiza o item recebido"""
    supabase.table("ocs_itens").update({
        "qtd_recebida": qtd_recebida,
        "recebido": True
    }).eq("id", item_id).execute()

    # Checa se todos os itens da OC foram recebidos
    itens = carregar_itens(oc_id)
    if itens["recebido"].all():
        supabase.table("ocs") \
            .update({"status": "recebida"}) \
            .eq("id", oc_id).execute()

def atualizar_oc_total(oc_id):
    """Recalcula total da OC após ajustes"""
    itens = carregar_itens(oc_id)
    total = float((itens["qtd_ajustada"] * itens["preco_custo"]).sum())

    supabase.table("ocs").update({
        "total_valor": total,
        "total_itens": len(itens),
        "atualizado_em": datetime.now().isoformat()
    }).eq("id", oc_id).execute()

# ==========================================================
# INTERFACE DA PÁGINA
# ==========================================================

st.title("📦 Histórico de Ordens de Compra")

tab1, tab2 = st.tabs(["📋 Todas as OCs", "📦 Detalhe da OC"])

# ==========================================================
# 1. LISTA DE TODAS AS OCs
# ==========================================================

with tab1:
    st.subheader("Lista de OCs")

    ocs = carregar_ocs()
    if ocs.empty:
        st.info("Nenhuma OC registrada ainda.")
    else:
        # filtros
        col1, col2, col3 = st.columns(3)
        empresa_filt = col1.selectbox("Empresa", ["TODAS", "ALIVVIA", "JCA"])
        status_filt = col2.selectbox("Status", ["TODOS", "pendente", "recebida", "cancelada"])
        fornecedor_filt = col3.text_input("Fornecedor (contém)")

        df = ocs.copy()

        if empresa_filt != "TODAS":
            df = df[df["empresa"] == empresa_filt]

        if status_filt != "TODOS":
            df = df[df["status"] == status_filt]

        if fornecedor_filt:
            df = df[df["fornecedor"].str.contains(fornecedor_filt.upper(), na=False)]

        st.dataframe(
            df[["numero", "fornecedor", "empresa", "status", "total_itens", "total_valor", "criado_em"]],
            use_container_width=True
        )

        st.markdown("### Abrir OC específica")
        oc_id = st.selectbox("Selecione a OC", df["id"].tolist())

# ==========================================================
# 2. DETALHE DA OC
# ==========================================================

with tab2:
    st.subheader("Detalhes da OC")

    if "oc_id" not in locals():
        st.info("Selecione uma OC na aba anterior.")
    else:
        oc = ocs[ocs["id"] == oc_id].iloc[0]
        st.markdown(f"### **OC Nº {oc['numero']} — {oc['fornecedor']}**")
        st.caption(f"Empresa: {oc['empresa']} • Criada em: {oc['criado_em']}")

        itens = carregar_itens(oc_id)

        if itens.empty:
            st.info("Nenhum item encontrado.")
        else:
            for _, row in itens.iterrows():
                with st.container(border=True):
                    st.markdown(f"**SKU:** {row['sku']}")
                    st.markdown(f"**Qtd Ajustada:** {row['qtd_ajustada']}")
                    st.markdown(f"**Preço custo:** R$ {row['preco_custo']:.2f}")

                    colA, colB = st.columns([1, 1])

                    qtd_recebida = colA.number_input(
                        "Quantidade recebida:",
                        min_value=0,
                        value=row["qtd_recebida"],
                        key=f"rec_{row['id']}"
                    )

                    if colB.button("Marcar como recebido", key=f"btn_{row['id']}"):
                        marcar_recebido(oc_id, row["id"], qtd_recebida)
                        st.success("Item atualizado!")
                        st.experimental_rerun()

            st.markdown("---")
            st.subheader("Exportação")

            if st.button("📄 Gerar PDF da OC"):
                st.warning("PDF será implementado na etapa final.")

