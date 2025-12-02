import streamlit as st
import pandas as pd
import datetime as dt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

st.title("📦 Ordem de Compra Oficial")

# -------------------------------------------------------------
# Recuperar OC base criada no passo anterior
# -------------------------------------------------------------
oc_base = st.session_state.get("oc_base", None)

if oc_base is None:
    st.error("Nenhuma Pré-OC encontrada. Volte para a Pré-OC.")
    st.stop()

fornecedor = oc_base["fornecedor"]
empresa = oc_base["empresa"]
df = oc_base["df"]


# -------------------------------------------------------------
# Número único da OC
# -------------------------------------------------------------
if "oc_counter" not in st.session_state:
    st.session_state.oc_counter = 1

numero_oc = f"OC-{dt.datetime.now().strftime('%Y%m%d')}-{st.session_state.oc_counter}"


# -------------------------------------------------------------
# Mostra resumo antes de gerar PDF
# -------------------------------------------------------------
st.subheader("📌 Dados da OC")

col1, col2, col3 = st.columns(3)
col1.write(f"**Empresa:** {empresa}")
col2.write(f"**Fornecedor:** {fornecedor}")
col3.write(f"**Número da OC:** {numero_oc}")

st.dataframe(df, use_container_width=True)


# -------------------------------------------------------------
# Gerar PDF
# -------------------------------------------------------------
def gerar_pdf(df, fornecedor, empresa, numero_oc):
    file_name = f"{numero_oc}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)

    width, height = A4

    y = height - 2*cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, "ORDEM DE COMPRA")
    y -= 1*cm

    c.setFont("Helvetica", 12)
    c.drawString(2*cm, y, f"Empresa: {empresa}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Fornecedor: {fornecedor}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Nº da OC: {numero_oc}")
    y -= 1*cm

    # Cabeçalho tabela
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "SKU")
    c.drawString(7*cm, y, "Qtd.")
    c.drawString(10*cm, y, "Conf. Receb.")
    y -= 0.6*cm
    c.line(2*cm, y, 18*cm, y)
    y -= 0.5*cm

    c.setFont("Helvetica", 10)

    for _, row in df.iterrows():
        if y < 3*cm:  # cria nova página se necessário
            c.showPage()
            y = height - 2*cm

        c.drawString(2*cm, y, str(row["SKU"]))
        c.drawString(7*cm, y, str(int(row["Compra_Sugerida"])))
        c.drawString(10*cm, y, "__________")  # espaço para escrever na conferência

        y -= 0.7*cm

    c.save()
    return file_name


# -------------------------------------------------------------
# Botão para gerar e baixar PDF
# -------------------------------------------------------------
if st.button("📄 Gerar PDF da OC"):
    pdf_path = gerar_pdf(df, fornecedor, empresa, numero_oc)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        "⬇ Baixar OC em PDF",
        data=pdf_bytes,
        file_name=pdf_path,
        mime="application/pdf"
    )

    # salva no histórico
    if "historico_oc" not in st.session_state:
        st.session_state.historico_oc = []

    st.session_state.historico_oc.append({
        "numero": numero_oc,
        "empresa": empresa,
        "fornecedor": fornecedor,
        "df": df,
        "pdf": pdf_bytes,
        "status": "PENDENTE"
    })

    st.session_state.oc_counter += 1

    st.success("OC gerada e salva no histórico!")


# -------------------------------------------------------------
# Histórico de OCs
# -------------------------------------------------------------
st.markdown("---")
st.subheader("📚 Histórico de OCs Emitidas")

hist = st.session_state.get("historico_oc", [])

if len(hist) == 0:
    st.info("Nenhuma OC emitida ainda.")
else:
    for oc in hist:
        with st.expander(f"{oc['numero']} — {oc['fornecedor']} — {oc['empresa']} — Status: {oc['status']}"):
            st.dataframe(oc["df"], use_container_width=True)

            c1, c2, c3 = st.columns(3)

            with c1:
                st.download_button(
                    "⬇ Baixar PDF",
                    data=oc["pdf"],
                    file_name=f"{oc['numero']}.pdf",
                    mime="application/pdf"
                )

            with c2:
                if st.button(f"Marcar como RECEBIDO — {oc['numero']}"):
                    oc["status"] = "RECEBIDO"
                    st.success("Atualizado!")

            with c3:
                if st.button(f"Excluir — {oc['numero']}"):
                    hist.remove(oc)
                    st.success("OC excluída.")
                    st.experimental_rerun()
