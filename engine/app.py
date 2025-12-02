import os
import pandas as pd

from normalizador import carregar_full, carregar_fisico, carregar_vendas
from kits import explodir_kits
from calculo import calcular_reposicao
from oc_engine import (
    init_db, gerar_numero_oc, salvar_oc,
    listar_ocs, marcar_recebida, gerar_pdf_oc
)


# =====================================================
# 1 — INICIALIZAR MÓDULOS ESSENCIAIS
# =====================================================

def iniciar_sistema():
    """
    Inicializa banco local e garante estrutura para funcionar.
    """
    init_db()
    print("✔ Sistema pronto para uso.")


# =====================================================
# 2 — CARREGAR UPLOADS
# =====================================================

def carregar_arquivos(full_path, fisico_path, vendas_path, kits_path):
    """
    Retorna todos os dataframes carregados.
    """
    df_full = carregar_full(full_path)
    df_fisico = carregar_fisico(fisico_path)
    df_vendas = carregar_vendas(vendas_path)

    # Kits (já convertido para DF fora do módulo)
    df_kits = pd.read_excel(kits_path)

    return df_full, df_fisico, df_vendas, df_kits


# =====================================================
# 3 — EXECUTAR CÁLCULO COMPLETO
# =====================================================

def executar_calculo(df_full, df_fisico, df_vendas, df_kits, horizonte, lead_time, crescimento):
    """
    Pipeline completo:
    1. Explode kits
    2. Consolida vendas/estoque
    3. Calcula quantidades sugeridas
    """
    vendas_exp = explodir_kits(df_vendas, df_kits)
    fisico_exp = explodir_kits(df_fisico, df_kits)
    full_exp = explodir_kits(df_full, df_kits)

    df_final = calcular_reposicao(
        vendas_exp, fisico_exp, full_exp,
        horizonte=horizonte,
        lead_time=lead_time,
        crescimento=crescimento
    )

    return df_final


# =====================================================
# 4 — CRIAR PRÉ OC
# =====================================================

def criar_pre_oc(df_calculo, fornecedor=None, empresa=None):
    """
    Filtra a sugestão de compra para preparar a OC final.
    Permite filtro por fornecedor e empresa.
    """

    df = df_calculo.copy()

    if fornecedor:
        df = df[df["Fornecedor"] == fornecedor]

    if empresa:
        df = df[df["Empresa"] == empresa]

    df = df[df["Compra_Sugerida"] > 0]

    return df[[
        "SKU", "Empresa", "Fornecedor",
        "Compra_Sugerida", "Preco_Custo", "Valor_Total_R$"
    ]]


# =====================================================
# 5 — GERAR OC FINAL
# =====================================================

def gerar_oc(df_pre, fornecedor, empresa, logo_path=None):
    """
    Cria número, salva no banco e gera PDF.
    """
    numero = gerar_numero_oc(fornecedor)

    df_pre = df_pre.rename(columns={
        "Compra_Sugerida": "Qtd_Ajustada",
        "Valor_Total_R$": "Valor_Ajustado_R$"
    })

    # Salvar no banco
    salvar_oc(numero, fornecedor, empresa, df_pre)

    # Gerar PDF
    pdf = gerar_pdf_oc(numero, fornecedor, empresa, df_pre, logo_path=logo_path)

    return numero, pdf


# =====================================================
# 6 — LISTAR OCs
# =====================================================

def listar_ocs_abertas():
    return listar_ocs(status="ABERTAS")


def listar_ocs_recebidas():
    return listar_ocs(status="RECEBIDAS")


# =====================================================
# 7 — MARCAR COMO RECEBIDA
# =====================================================

def receber_oc(numero):
    marcar_recebida(numero)
