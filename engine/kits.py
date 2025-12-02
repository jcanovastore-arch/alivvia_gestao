import pandas as pd
from dataclasses import dataclass
from .normalizador import norm_sku, normalize_cols, br_to_float


@dataclass
class Catalogo:
    catalogo_simples: pd.DataFrame   # SKU, fornecedor, status
    kits_reais: pd.DataFrame         # kit_sku, component_sku, qty


def carregar_padrao_excel(xls_bytes: bytes) -> Catalogo:
    """
    Lê o XLS padrão contendo:
    - Aba CATALOGO
    - Aba KITS
    """
    xls = pd.ExcelFile(xls_bytes)

    # --- Carregar catálogo simples ---
    aba_cat = None
    for name in xls.sheet_names:
        if "CATALOGO" in name.upper():
            aba_cat = name
            break
    if not aba_cat:
        raise ValueError("A planilha não contém aba CATALOGO.")

    df_cat = pd.read_excel(xls, aba_cat, dtype=str, keep_default_na=False)
    df_cat = normalize_cols(df_cat)

    possiveis_cat = {
        "component_sku": ["component_sku", "sku", "codigo", "produto"],
        "fornecedor": ["fornecedor", "supplier"],
        "status_reposicao": ["status_reposicao", "status"]
    }

    rename_c = {}
    for col_dest, poss in possiveis_cat.items():
        for p in poss:
            if p in df_cat.columns:
                rename_c[p] = col_dest
                break

    df_cat = df_cat.rename(columns=rename_c)
    df_cat["component_sku"] = df_cat["component_sku"].map(norm_sku)
    df_cat["fornecedor"] = df_cat["fornecedor"].fillna("").astype(str)
    df_cat["status_reposicao"] = df_cat["status_reposicao"].fillna("").astype(str)

    # Remove SKUs com status "nao_repor"
    mask_repor = ~df_cat["status_reposicao"].str.lower().str.contains("nao_repor")
    df_cat = df_cat[mask_repor].copy()

    # --- Carregar kits ---
    aba_kits = None
    for name in xls.sheet_names:
        if "KIT" in name.upper():
            aba_kits = name
            break
    if not aba_kits:
        raise ValueError("A planilha não contém aba KITS.")

    df_kits = pd.read_excel(xls, aba_kits, dtype=str, keep_default_na=False)
    df_kits = normalize_cols(df_kits)

    possiveis_kits = {
        "kit_sku": ["kit_sku", "sku_kit", "kit"],
        "component_sku": ["component_sku", "sku_componente", "componente"],
        "qty": ["qty", "quantidade", "qtd", "qtd_por_kit"]
    }

    rename_k = {}
    for col_dest, poss in possiveis_kits.items():
        for p in poss:
            if p in df_kits.columns:
                rename_k[p] = col_dest
                break

    df_kits = df_kits.rename(columns=rename_k)
    df_kits["kit_sku"] = df_kits["kit_sku"].map(norm_sku)
    df_kits["component_sku"] = df_kits["component_sku"].map(norm_sku)
    df_kits["qty"] = df_kits["qty"].map(br_to_float).fillna(0).astype(int)

    # Remove linhas inválidas
    df_kits = df_kits[df_kits["qty"] > 0]

    # Remover duplicatas
    df_kits = df_kits.drop_duplicates(subset=["kit_sku", "component_sku"])

    return Catalogo(catalogo_simples=df_cat.reset_index(drop=True),
                    kits_reais=df_kits.reset_index(drop=True))


def construir_kits_efetivo(cat: Catalogo) -> pd.DataFrame:
    """
    - Mantém kits reais
    - Adiciona componentes simples como "kits unitários"
    """
    df_k = cat.kits_reais.copy()

    componentes = set(cat.catalogo_simples["component_sku"])
    kits_definidos = set(df_k["kit_sku"])

    alias = []
    for sku in componentes:
        if sku not in kits_definidos:
            alias.append((sku, sku, 1))  # SKU simples → ele mesmo

    if alias:
        alias_df = pd.DataFrame(alias, columns=["kit_sku", "component_sku", "qty"])
        df_k = pd.concat([df_k, alias_df], ignore_index=True)

    df_k = df_k.drop_duplicates(subset=["kit_sku", "component_sku"])
    return df_k


def explodir_kits(df_base: pd.DataFrame, kits: pd.DataFrame,
                  sku_col: str, qtd_col: str) -> pd.DataFrame:
    """
    Recebe vendas FULL/físicas ou Shopee e explode para nível componente.
    """
    base = df_base.copy()
    base["kit_sku"] = base[sku_col].map(norm_sku)
    base["qtd"] = base[qtd_col].astype(int)

    merged = base.merge(kits, on="kit_sku", how="left")
    merged = merged.dropna(subset=["component_sku"]).copy()

    merged["qty"] = merged["qty"].astype(int)
    merged["resultado"] = merged["qtd"] * merged["qty"]

    out = merged.groupby("component_sku", as_index=False)["resultado"].sum()
    out = out.rename(columns={"component_sku": "SKU",
                              "resultado": "Quantidade"})

    return out
