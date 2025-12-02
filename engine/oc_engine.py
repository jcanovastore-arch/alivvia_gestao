import sqlite3
import datetime as dt
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


# =====================================================
# 1 — BANCO LOCAL (db/ocs.db)
# =====================================================

DB_PATH = os.path.join("db", "ocs.db")

def init_db():
    if not os.path.exists("db"):
        os.makedirs("db")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            fornecedor TEXT,
            empresa TEXT,
            criado_em TEXT,
            recebido INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS oc_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oc_numero TEXT,
            sku TEXT,
            qtd INTEGER,
            preco REAL,
            valor REAL
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# 2 — GERAR NÚMERO ÚNICO DE OC
# =====================================================

def gerar_numero_oc(fornecedor: str) -> str:
    """
    Exemplo: OC-DRAGONFIT-20251201-001
    """
    data = dt.datetime.now().strftime("%Y%m%d")
    fornecedor_clean = fornecedor.upper().replace(" ", "")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM ocs WHERE criado_em LIKE ?", (f"{data}%",))
    count = cur.fetchone()[0] + 1
    conn.close()

    return f"OC-{fornecedor_clean}-{data}-{count:03d}"


# =====================================================
# 3 — SALVAR OC NO BANCO
# =====================================================

def salvar_oc(numero, fornecedor, empresa, df_itens):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("INSERT INTO ocs (numero, fornecedor, empresa, criado_em) VALUES (?, ?, ?, ?)",
                (numero, fornecedor, empresa, dt.datetime.now().isoformat()))

    for _, row in df_itens.iterrows():
        cur.execute("""
            INSERT INTO oc_itens (oc_numero, sku, qtd, preco, valor)
            VALUES (?, ?, ?, ?, ?)
        """, (numero, row["SKU"], int(row["Qtd_Ajustada"]), float(row["Preco_Custo"]), float(row["Valor_Ajustado_R$"])))

    conn.commit()
    conn.close()


# =====================================================
# 4 — LISTAR OCs EXISTENTES
# =====================================================

def listar_ocs(status="ABERTAS"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if status == "ABERTAS":
        cur.execute("SELECT numero, fornecedor, empresa, criado_em FROM ocs WHERE recebido = 0")
    else:
        cur.execute("SELECT numero, fornecedor, empresa, criado_em FROM ocs WHERE recebido = 1")

    out = cur.fetchall()
    conn.close()
    return out


# =====================================================
# 5 — MARCAR OC COMO RECEBIDA
# =====================================================

def marcar_recebida(oc_numero):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE ocs SET recebido = 1 WHERE numero = ?", (oc_numero,))
    conn.commit()
    conn.close()


# =====================================================
# 6 — GERAR PDF PROFISSIONAL
# =====================================================

def gerar_pdf_oc(oc_numero, fornecedor, empresa, df_itens, logo_path=None):
    """
    Gera uma OC bonita: Logo + Tabela + Campo de conferência.
    Output: pdfs/<OC_NUMERO>.pdf
    """

    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

    filename = f"pdfs/{oc_numero}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Título
    title = Paragraph(f"<b>ORDEM DE COMPRA — {oc_numero}</b>", styles['Title'])
    st_fornecedor = Paragraph(f"<b>Fornecedor:</b> {fornecedor}", styles['Normal'])
    st_empresa = Paragraph(f"<b>Empresa:</b> {empresa}", styles['Normal'])
    st_data = Paragraph(f"<b>Data de Emissão:</b> {dt.datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])

    story.append(title)
    story.append(Spacer(1, 12))
    story.append(st_fornecedor)
    story.append(st_empresa)
    story.append(st_data)
    story.append(Spacer(1, 20))

    # Caso tenha logo
    if logo_path and os.path.exists(logo_path):
        from reportlab.platypus import Image
        story.append(Image(logo_path, width=120, height=60))
        story.append(Spacer(1, 20))

    # Tabela
    data = [["SKU", "Qtd Solicitada", "Preço Unit", "Total (R$)", "Conferência Recebido"]]

    for _, row in df_itens.iterrows():
        data.append([
            row["SKU"],
            int(row["Qtd_Ajustada"]),
            f"R$ {row['Preco_Custo']:.2f}",
            f"R$ {row['Valor_Ajustado_R$']:.2f}",
            "____________________"
        ])

    table = Table(data, colWidths=[100, 90, 80, 80, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    story.append(table)
    story.append(Spacer(1, 30))

    doc.build(story)

    return filename
