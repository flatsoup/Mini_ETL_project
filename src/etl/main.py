from __future__ import annotations
import argparse
from pathlib import Path
from .utils import load_config, setup_logger
from .extract import fetch_html, parse_table
from .transform import transform, load_exchange_rates
from .load import to_csv, init_db, to_sqlite

def run(cfg_path: Path) -> None:
    cfg = load_config(cfg_path)
    logger = setup_logger(Path(cfg["paths"]["logs_dir"]))
    logger.info("START: Banks ETL v1.0")

    # Extract
    html = fetch_html(
        url=cfg["source"]["url"],
        user_agent=cfg["extract"]["user_agent"],
        timeout=cfg["extract"]["timeout_sec"],
        retries=cfg["extract"]["retries"],
        raw_out=Path(cfg["paths"]["raw_html"]),
        logger=logger,
    )
    df_raw = parse_table(html, logger)

    # Transform
    rates = load_exchange_rates(cfg["transform"]["exchange_rate_csv"])
    df_tr = transform(df_raw, cfg["transform"]["currencies"], rates, logger)

    # Load
    to_csv(df_tr, Path(cfg["load"]["csv_output"]), logger)
    init_db(Path(cfg["load"]["db_path"]), cfg["load"]["table_name"], logger)
    to_sqlite(df_tr, Path(cfg["load"]["db_path"]), cfg["load"]["table_name"], logger)

    # Простенький отчёт по качеству
    report = {
        "rows": int(len(df_tr)),
        "unique_names": int(df_tr["Name"].nunique()),
        "usd_min": float(df_tr["MC_USD_Billion"].min()),
        "usd_max": float(df_tr["MC_USD_Billion"].max()),
        "nulls_total": int(df_tr.isna().sum().sum()),
    }
    logger.info(f"DQ REPORT: {report}")
    print("Done. See logs for details.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Banks ETL v1.0")
    ap.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = ap.parse_args()
    run(Path(args.config))