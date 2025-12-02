import pandas as pd
import numpy as np
from unidecode import unidecode

def norm_sku(x: str) -> str:
    """Normaliza SKU removendo acentos, espaços e colocando em maiúsculas."""
    if pd.isna(x):
        return ""
    return unidecode(str(x)).strip().upper()

def br_to_float(x):
    """Converte valores do padrão brasileiro para float."""
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.integer, np.floating)):
        return float(x)

    s = str(x).strip()
    if s == "":
        return np.nan

    s = (
        s.replace("R$", "")
         .replace(".", "")
         .replace(" ", "")
         .replace(",", ".")
    )

    try:
        return float(s)
    except:
        return np.nan

def norm_header(s: str) -> str:
    """Normaliza nomes de colunas para um formato padrão."""
    if s is None:
        return ""
    s = unidecode(s).lower().strip()
    for ch in " -()/\\[].,;:":
        s = s.replace(ch, "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")

def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica normalização de colunas."""
    df = df.copy()
    df.columns = [norm_header(c) for c in df.columns]
    return df
