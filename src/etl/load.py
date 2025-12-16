from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd


def to_csv(df: pd.DataFrame, csv_path: Path, logger) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    logger.info(f"LOAD: saved CSV -> {csv_path}")


def init_db(db_path: Path, table: str, logger) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                Rank INTEGER,
                Name TEXT NOT NULL,
                MC_USD_Billion REAL NOT NULL,
                MC_EUR_Billion REAL,
                MC_GBP_Billion REAL,
                MC_INR_Billion REAL
            )
            """
        )
        cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_name ON {table}(name)")
        conn.commit()
    logger.info(f"LOAD: ensured table/index in DB {db_path}")


def to_sqlite(df: pd.DataFrame, db_path: Path, table: str, logger) -> None:
    with sqlite3.connect(db_path) as conn:
        # Идемпотентная перезаливка для простоты v1.0
        conn.execute(f"DELETE FROM {table}")
        df.to_sql(table, conn, if_exists="append", index=False)
        conn.commit()
    logger.info(f"LOAD: saved {len(df)} rows -> {db_path}:{table}")