from __future__ import annotations
from pathlib import Path
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

REQUIRED_COLS = {"Bank name", "Market cap (US$ billion)"}


def fetch_html(url: str, user_agent: str, timeout: int, retries: int, raw_out: Path, logger) -> str:
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": user_agent})
            resp.raise_for_status()
            html = resp.text
            raw_out.write_text(html, encoding="utf-8")
            logger.info(f"EXTRACT: fetched HTML (len={len(html)}). Attempt {attempt}/{retries}.")
            return html
        except Exception as e:
            last_err = e
            logger.warning(f"EXTRACT: attempt {attempt}/{retries} failed: {e}")
            time.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"EXTRACT failed after {retries} attempts: {last_err}")


def parse_table(html: str, logger) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table", {"class": "wikitable"})
    if not tables:
        raise ValueError("No wikitable found on page")

    # Ищем таблицу, содержащую нужные заголовки
    for idx, t in enumerate(tables):
        df = pd.read_html(StringIO(str(t)))[0]
        if REQUIRED_COLS.issubset(set(map(str, df.columns))):
            logger.info(f"EXTRACT: matched table index {idx} with required columns.")
            return df

    raise ValueError("Required columns not found in any wikitable")