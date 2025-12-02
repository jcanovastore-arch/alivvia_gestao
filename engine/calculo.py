import numpy as np
import pandas as pd
from .kits import construir_kits_efetivo, explodir_kits, Catalogo
from .normalizador import norm_sku


def preparar_full(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza FULL → SKU, vendas_60d, estoque_full, em_transito."""
    out = df.copy()
    out["SKU"] = out["SKU"].map(norm_sku)
    out["Vendas_60d"] = out["Vendas_60d"].astype(int)
    out["Estoque_Full"] = out["Estoque_Full"].astype(int)
    out["Em_Transito"] = out["Em_Transito"].astype(int)
    return out


def preparar_fisico(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza Estoque Físico → SKU, estoque, custo."""
    out = df.copy()
    out["SKU"] = out["SKU"].map(norm_sku)
    out["Estoque_Fisico"] = out["Estoque_Fisico"].fillna(0).astype(int)
    out["Preco"] = out["Preco"].fillna(0.0).astype(float)
    return out


def preparar_vendas(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza Shopee → SKU, quantidade."""
    out = df.copy()
    out["SKU"] = out["SKU"].map(norm_sku)
    out["Quantidade"] = out["Quantidade"].astype(int)
    return out


def calcular_reposicao(full_df, fisico_df, vendas_df,
                       cat: Catalogo, horizonte=60,
                       crescimento=0.0, lead_time=0):
    """
    Motor principal da reposição.
    """

    # -----------------------------
    # 1. Preparar dados
    # -----------------------------
    full = preparar_full(full_df)
    fisico = preparar_fisico(fisico_df)
    vendas = preparar_vendas(vendas_df)

    # -----------------------------
    # 2. Construir matriz de kits
    # -----------------------------
    kits = construir_kits_efetivo(cat)

    # -----------------------------
    # 3. Explodir as vendas FULL
    # -----------------------------
    full_exp = explodir_kits(
        full[["SKU", "Vendas_60d"]].rename(columns={"SKU": "kit_sku",
                                                    "Vendas_60d": "Qtd"}),
        kits,
        "kit_sku",
        "Qtd"
    ).rename(columns={"Quantidade": "ML_60d"})

    # -----------------------------
    # 4. Explodir as vendas Shopee
    # -----------------------------
    shopee_exp = explodir_kits(
        vendas[["SKU", "Quantidade"]].rename(columns={"SKU": "kit_sku",
                                                      "Quantidade": "Qtd"}),
        kits,
        "kit_sku",
        "Qtd"
    ).rename(columns={"Quantidade": "Shopee_60d"})

    # -----------------------------
    # 5. Catálogo básico
    # -----------------------------
    cat_df = cat.catalogo_simples.rename(
        columns={"component_sku": "SKU"}
    ).copy()

    # -----------------------------
    # 6. Anexar vendas ao catálogo
    # -----------------------------
    base = cat_df.merge(full_exp, on="SKU", how="left") \
                 .merge(shopee_exp, on="SKU", how="left")

    base["ML_60d"] = base["ML_60d"].fillna(0).astype(int)
    base["Shopee_60d"] = base["Shopee_60d"].fillna(0).astype(int)
    base["Vendas_60d_Total"] = base["ML_60d"] + base["Shopee_60d"]

    # -----------------------------
    # 7. Juntar Estoque Físico
    # -----------------------------
    base = base.merge(fisico[["SKU", "Estoque_Fisico", "Preco"]],
                      on="SKU",
                      how="left")

    base["Estoque_Fisico"] = base["Estoque_Fisico"].fillna(0).astype(int)
    base["Preco"] = base["Preco"].fillna(0.0).astype(float)

    # -----------------------------
    # 8. Juntar Estoque FULL
    # -----------------------------
    base = base.merge(
        full[["SKU", "Estoque_Full", "Em_Transito"]],
        on="SKU",
        how="left"
    )

    base["Estoque_Full"] = base["Estoque_Full"].fillna(0).astype(int)
    base["Em_Transito"] = base["Em_Transito"].fillna(0).astype(int)

    # -----------------------------
    # 9. Cálculo de alvo de FULL
    # -----------------------------
    fator_crescimento = (1 + crescimento / 100.0) ** (horizonte / 30.0)

    full_calc = full.copy()
    full_calc["vendas_dia"] = full_calc["Vendas_60d"] / 60.0
    full_calc["alvo"] = np.round(
        full_calc["vendas_dia"] * (horizonte + lead_time) * fator_crescimento
    ).astype(int)

    full_calc["oferta"] = (full_calc["Estoque_Full"] +
                           full_calc["Em_Transito"]).astype(int)

    full_calc["envio_desejado"] = \
        (full_calc["alvo"] - full_calc["oferta"]).clip(lower=0).astype(int)

    # Explode necessidades
    necessidade = explodir_kits(
        full_calc[["SKU", "envio_desejado"]].rename(
            columns={"SKU": "kit_sku", "envio_desejado": "Qtd"}),
        kits,
        "kit_sku",
        "Qtd"
    ).rename(columns={"Quantidade": "Necessidade"})

    base = base.merge(necessidade, on="SKU", how="left")
    base["Necessidade"] = base["Necessidade"].fillna(0).astype(int)

    # -----------------------------
    # 10. Cálculo de reserva física mínima
    # -----------------------------
    base["Demanda_dia"] = base["Vendas_60d_Total"] / 60.0
    base["Reserva_30d"] = np.round(base["Demanda_dia"] * 30).astype(int)

    # Quanto sobra no físico
    base["Folga_Fisico"] = (base["Estoque_Fisico"] -
                            base["Reserva_30d"]).clip(lower=0).astype(int)

    # -----------------------------
    # 11. Compra sugerida final
    # -----------------------------
    base["Compra_Sugerida"] = (base["Necessidade"] -
                               base["Folga_Fisico"]).clip(lower=0).astype(int)

    # Valor da compra
    base["Valor_Compra_R$"] = (base["Compra_Sugerida"].astype(float) *
                               base["Preco"].astype(float)).round(2)

    # -----------------------------
    # 12. Resultado final
    # -----------------------------
    cols = [
        "SKU", "fornecedor",
        "Vendas_60d_Total",
        "ML_60d", "Shopee_60d",
        "Estoque_Full", "Em_Transito",
        "Estoque_Fisico", "Preco",
        "Necessidade", "Folga_Fisico",
        "Compra_Sugerida", "Valor_Compra_R$"
    ]

    return base[cols].copy().reset_index(drop=True)
