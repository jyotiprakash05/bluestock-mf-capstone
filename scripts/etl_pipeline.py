"""
etl_pipeline.py
Bluestock Fintech | Mutual Fund Analytics Capstone
Day 2: Clean all 10 datasets and load into SQLite database.

Usage:
    python scripts/etl_pipeline.py
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
RAW_DIR   = BASE_DIR / "data" / "raw"
PROC_DIR  = BASE_DIR / "data" / "processed"
DB_DIR    = BASE_DIR / "data" / "db"
SQL_DIR   = BASE_DIR / "sql"

PROC_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH   = DB_DIR / "bluestock_mf.db"
ENGINE    = create_engine(f"sqlite:///{DB_PATH}")

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"  {msg}")

def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def save(df: pd.DataFrame, name: str) -> None:
    path = PROC_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    log(f"Saved → data/processed/{name}.csv  ({len(df):,} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — CLEAN DATASETS
# ─────────────────────────────────────────────────────────────────────────────

def clean_fund_master() -> pd.DataFrame:
    section("1/10  Cleaning: fund_master")
    df = pd.read_csv(RAW_DIR / "01_fund_master.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["fund_house"] = df["fund_house"].str.strip()
    df["scheme_name"] = df["scheme_name"].str.strip()

    # Validate expense ratio range 0.1% – 2.5%
    if "expense_ratio_pct" in df.columns:
        bad = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
        if not bad.empty:
            log(f"⚠ {len(bad)} rows with unusual expense_ratio — review manually")

    df.drop_duplicates(subset=["amfi_code"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    log(f"Clean shape: {df.shape}  | Unique funds: {df['amfi_code'].nunique()}")
    save(df, "clean_fund_master")
    return df


def clean_nav_history() -> pd.DataFrame:
    section("2/10  Cleaning: nav_history")
    df = pd.read_csv(RAW_DIR / "02_nav_history.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(subset=["date"], inplace=True)

    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    # Remove zero or negative NAV
    invalid = df[df["nav"] <= 0]
    if not invalid.empty:
        log(f"⚠ Dropping {len(invalid)} rows with NAV ≤ 0")
    df = df[df["nav"] > 0].copy()

    df.drop_duplicates(subset=["amfi_code", "date"], inplace=True)
    df.sort_values(["amfi_code", "date"], inplace=True)

    # Forward-fill missing NAV for weekends/holidays per fund
    df = (df.groupby("amfi_code", group_keys=False)
            .apply(lambda g: g.set_index("date")
                               .reindex(pd.bdate_range(g["date"].min(), g["date"].max()))
                               .ffill()
                               .reset_index()
                               .rename(columns={"index": "date"}))
    )
    df["amfi_code"] = df["amfi_code"].ffill()

    # Compute daily return %
    df["daily_return_pct"] = (df.groupby("amfi_code")["nav"]
                                .pct_change()
                                .round(6))

    df.reset_index(drop=True, inplace=True)
    log(f"Clean shape: {df.shape}")
    log(f"Date range : {df['date'].min().date()} → {df['date'].max().date()}")
    save(df, "clean_nav_history")
    return df


def clean_aum() -> pd.DataFrame:
    section("3/10  Cleaning: aum_by_fund_house")
    df = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["fund_house"] = df["fund_house"].str.strip()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["aum_crore"] = pd.to_numeric(df["aum_crore"], errors="coerce")
    df.dropna(subset=["aum_crore"], inplace=True)
    df.drop_duplicates(inplace=True)

    log(f"Clean shape: {df.shape} | Fund houses: {df['fund_house'].nunique()}")
    save(df, "clean_aum_by_fund_house")
    return df


def clean_sip_inflows() -> pd.DataFrame:
    section("4/10  Cleaning: monthly_sip_inflows")
    df = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["month"] = df["month"].astype(str).str.strip()
    df["sip_inflow_crore"] = pd.to_numeric(df["sip_inflow_crore"], errors="coerce")
    df.dropna(subset=["sip_inflow_crore"], inplace=True)
    df.drop_duplicates(subset=["month"], inplace=True)
    df.sort_values("month", inplace=True)

    log(f"Clean shape: {df.shape} | Months: {df['month'].min()} → {df['month'].max()}")
    save(df, "clean_monthly_sip_inflows")
    return df


def clean_category_inflows() -> pd.DataFrame:
    section("5/10  Cleaning: category_inflows")
    df = pd.read_csv(RAW_DIR / "05_category_inflows.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)
    log(f"Clean shape: {df.shape}")
    save(df, "clean_category_inflows")
    return df


def clean_folio_count() -> pd.DataFrame:
    section("6/10  Cleaning: industry_folio_count")
    df = pd.read_csv(RAW_DIR / "06_industry_folio_count.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)
    log(f"Clean shape: {df.shape}")
    save(df, "clean_industry_folio_count")
    return df


def clean_scheme_performance() -> pd.DataFrame:
    section("7/10  Cleaning: scheme_performance")
    df = pd.read_csv(RAW_DIR / "07_scheme_performance.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()

    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "sharpe_ratio", "sortino_ratio", "alpha", "beta",
        "std_dev_ann_pct", "max_drawdown_pct"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag unusual Sharpe ratios
    if "sharpe_ratio" in df.columns:
        neg_sharpe = df[df["sharpe_ratio"] < 0]
        if not neg_sharpe.empty:
            log(f"ℹ {len(neg_sharpe)} funds have negative Sharpe ratio (underperforming risk-free rate)")

    df.drop_duplicates(subset=["amfi_code"], inplace=True)
    log(f"Clean shape: {df.shape}")
    save(df, "clean_scheme_performance")
    return df


def clean_transactions() -> pd.DataFrame:
    section("8/10  Cleaning: investor_transactions")
    df = pd.read_csv(RAW_DIR / "08_investor_transactions.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df.dropna(subset=["transaction_date"], inplace=True)

    # Standardise transaction_type
    df["transaction_type"] = (df["transaction_type"]
                              .str.strip()
                              .str.title()
                              .replace({"Sip": "SIP", "Lumpsum": "Lumpsum", "Redemption": "Redemption"}))

    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df = df[df["amount_inr"] > 0].copy()

    # Standardise KYC status
    if "kyc_status" in df.columns:
        df["kyc_status"] = df["kyc_status"].str.strip().str.title()

    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    log(f"Clean shape: {df.shape}")
    log(f"Transaction types: {df['transaction_type'].value_counts().to_dict()}")
    save(df, "clean_investor_transactions")
    return df


def clean_portfolio_holdings() -> pd.DataFrame:
    section("9/10  Cleaning: portfolio_holdings")
    df = pd.read_csv(RAW_DIR / "09_portfolio_holdings.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    if "weight_pct" in df.columns:
        df["weight_pct"] = pd.to_numeric(df["weight_pct"], errors="coerce")
        df = df[df["weight_pct"] > 0].copy()

    df.drop_duplicates(inplace=True)
    log(f"Clean shape: {df.shape}")
    save(df, "clean_portfolio_holdings")
    return df


def clean_benchmark_indices() -> pd.DataFrame:
    section("10/10  Cleaning: benchmark_indices")
    df = pd.read_csv(RAW_DIR / "10_benchmark_indices.csv", low_memory=False)
    log(f"Raw shape: {df.shape}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(subset=["date"], inplace=True)
    df.drop_duplicates(inplace=True)
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    log(f"Clean shape: {df.shape} | Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    save(df, "clean_benchmark_indices")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — CREATE DATABASE SCHEMA
# ─────────────────────────────────────────────────────────────────────────────

def create_schema() -> None:
    section("Creating SQLite Schema")
    schema_path = SQL_DIR / "schema.sql"
    with sqlite3.connect(DB_PATH) as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
    log(f"✓ Schema created → {DB_PATH.name}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — LOAD INTO DATABASE
# ─────────────────────────────────────────────────────────────────────────────

def load_to_db(df: pd.DataFrame, table: str, if_exists: str = "replace") -> None:
    df.to_sql(table, ENGINE, if_exists=if_exists, index=False)
    log(f"✓ Loaded {len(df):,} rows → {table}")


def load_all_to_db(datasets: dict) -> None:
    section("Loading cleaned data into SQLite")

    table_map = {
        "fund_master"         : ("dim_fund",           "amfi_code"),
        "nav_history"         : ("fact_nav",            None),
        "aum_by_fund_house"   : ("fact_aum",            None),
        "monthly_sip_inflows" : ("fact_sip_industry",   None),
        "category_inflows"    : ("fact_category_inflows", None),
        "folio_count"         : ("fact_folio_count",    None),
        "scheme_performance"  : ("fact_performance",    None),
        "transactions"        : ("fact_transactions",   None),
        "portfolio_holdings"  : ("fact_portfolio",      None),
        "benchmark_indices"   : ("fact_benchmark",      None),
    }

    for key, (table, _) in table_map.items():
        if key in datasets and datasets[key] is not None:
            load_to_db(datasets[key], table)
        else:
            log(f"⚠ Skipping {table} — dataset not available")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — VERIFY DATABASE
# ─────────────────────────────────────────────────────────────────────────────

def verify_db() -> None:
    section("Database Verification")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        log(f"Tables in database: {[t[0] for t in tables]}")
        print()
        for (table,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cursor.fetchone()[0]
            log(f"  {table:<35} {count:>8,} rows")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n" + "█"*60)
    print("  BLUESTOCK FINTECH — Day 2: ETL Pipeline")
    print("█"*60)

    # Step 1: Clean all datasets
    datasets = {
        "fund_master"        : clean_fund_master(),
        "nav_history"        : clean_nav_history(),
        "aum_by_fund_house"  : clean_aum(),
        "monthly_sip_inflows": clean_sip_inflows(),
        "category_inflows"   : clean_category_inflows(),
        "folio_count"        : clean_folio_count(),
        "scheme_performance" : clean_scheme_performance(),
        "transactions"       : clean_transactions(),
        "portfolio_holdings" : clean_portfolio_holdings(),
        "benchmark_indices"  : clean_benchmark_indices(),
    }

    # Step 2: Create DB schema
    create_schema()

    # Step 3: Load into DB
    load_all_to_db(datasets)

    # Step 4: Verify
    verify_db()

    section("ETL Complete ✓")
    log(f"Database saved → {DB_PATH}")
    log("Next step → python scripts/run_queries.py")
    print()


if __name__ == "__main__":
    main()
