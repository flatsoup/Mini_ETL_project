from __future__ import annotations
import pandas as pd
import numpy as np

RENAME_MAP = {
    "Bank name": "Name",
    "Market cap (US$ billion)": "MC_USD_Billion",
}


class TransformError(Exception):
    pass

def _clean_usd(col: pd.Series) -> pd.Series:
    s = (col.astype(str)
           .str.replace("\n", "", regex=False)
           .str.replace(",", "", regex=False)
         )
    out = pd.to_numeric(s, errors="coerce")
    if out.isna().any():
        bad = out.isna().sum()
        raise TransformError(f"Found {bad} non-numeric market cap values")
    if (out < 0).any():
        raise TransformError("Negative market cap encountered")
    return out


def load_exchange_rates(csv_path: str) -> dict:
    df_rates = pd.read_csv(csv_path)
    if {"Currency", "Rate"} - set(df_rates.columns):
        raise TransformError("exchange_rate.csv must contain Currency,Rate")
    d = df_rates.set_index("Currency")["Rate"].to_dict()
    return d


def transform(df: pd.DataFrame, currencies: list[str], exchange_rates: dict, logger) -> pd.DataFrame:
    # Переименуем и оставим нужное
    if not set(RENAME_MAP.keys()).issubset(df.columns):
        raise TransformError("Input dataframe missing expected columns")

    df = df.rename(columns=RENAME_MAP)[list(RENAME_MAP.values()) + [c for c in df.columns if c not in RENAME_MAP]]

    # Очистка и типы
    df["MC_USD_Billion"] = _clean_usd(df["MC_USD_Billion"])  # float, >=0

    # Валюты
    missing = set(currencies) - set(exchange_rates.keys())
    if missing:
        raise TransformError(f"Missing exchange rates for: {sorted(missing)}")

    for cur in currencies:
        col = f"MC_{cur}_Billion"
        df[col] = np.round(df["MC_USD_Billion"] * float(exchange_rates[cur]), 2)

    # Мини-проверки качества
    if df["Name"].isna().any() or df["Name"].eq("").any():
        raise TransformError("Blank bank names detected")

    logger.info(
        "TRANSFORM: rows=%d, USD[min=%.2f, max=%.2f]",
        len(df), float(df["MC_USD_Billion"].min()), float(df["MC_USD_Billion"].max())
    )
    return df