"""
data_ingestion.py
Bluestock Fintech | Mutual Fund Analytics Capstone
Day 1: Load all 10 CSV datasets and validate structure.

Usage:
    python scripts/data_ingestion.py
"""

import os
import pandas as pd
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE_DIR / "data" / "raw"
PROC_DIR   = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ── Dataset registry ─────────────────────────────────────────────────────────
DATASETS = {
    "01_fund_master"          : "Master list of 40 fund schemes",
    "02_nav_history"          : "Daily NAV for all 40 schemes (Jan 2022 – May 2026)",
    "03_aum_by_fund_house"    : "Quarterly AUM by fund house",
    "04_monthly_sip_inflows"  : "Monthly SIP inflow data",
    "05_category_inflows"     : "Net inflows by fund category",
    "06_industry_folio_count" : "Total MF folios by type",
    "07_scheme_performance"   : "1yr/3yr/5yr returns + risk metrics",
    "08_investor_transactions": "SIP / Lumpsum / Redemption transactions",
    "09_portfolio_holdings"   : "Top equity holdings per fund",
    "10_benchmark_indices"    : "Daily closing values for benchmark indices",
}


def load_dataset(name: str) -> pd.DataFrame | None:
    """Load a CSV from data/raw/ and return a DataFrame."""
    path = RAW_DIR / f"{name}.csv"
    if not path.exists():
        print(f"  [MISSING] {path.name} — place the file in data/raw/ and re-run.")
        return None
    df = pd.read_csv(path, low_memory=False)
    return df


def print_summary(name: str, df: pd.DataFrame, description: str) -> None:
    """Print shape, dtypes, and first 2 rows for a dataset."""
    print(f"\n{'='*60}")
    print(f"  {name}.csv")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"  Shape   : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  Columns : {list(df.columns)}")
    print(f"  Dtypes  :\n{df.dtypes.to_string()}")
    nulls = df.isnull().sum()
    if nulls.any():
        print(f"  Nulls   :\n{nulls[nulls > 0].to_string()}")
    else:
        print("  Nulls   : None ✓")
    print(f"\n  Sample (first 2 rows):\n{df.head(2).to_string()}")


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> None:
    """Check all AMFI codes in nav_history exist in fund_master."""
    print(f"\n{'='*60}")
    print("  AMFI CODE VALIDATION")
    print(f"{'='*60}")
    master_codes = set(fund_master["amfi_code"].astype(str))
    nav_codes    = set(nav_history["amfi_code"].astype(str))
    missing      = nav_codes - master_codes
    extra        = master_codes - nav_codes
    if not missing:
        print("  ✓ All NAV amfi_codes exist in fund_master.")
    else:
        print(f"  ⚠ Codes in nav_history NOT in fund_master ({len(missing)}): {missing}")
    if extra:
        print(f"  ℹ Codes in fund_master with no NAV data ({len(extra)}): {extra}")


def main() -> None:
    print("\n" + "█"*60)
    print("  BLUESTOCK FINTECH — Day 1: Data Ingestion")
    print("█"*60)

    loaded = {}
    for name, desc in DATASETS.items():
        df = load_dataset(name)
        if df is not None:
            print_summary(name, df, desc)
            loaded[name] = df

    # ── AMFI code cross-validation ────────────────────────────────────────────
    if "01_fund_master" in loaded and "02_nav_history" in loaded:
        validate_amfi_codes(loaded["01_fund_master"], loaded["02_nav_history"])

    # ── Fund master quick stats ───────────────────────────────────────────────
    if "01_fund_master" in loaded:
        fm = loaded["01_fund_master"]
        print(f"\n{'='*60}")
        print("  FUND MASTER QUICK STATS")
        print(f"{'='*60}")
        print(f"  Unique fund houses  : {fm['fund_house'].nunique()}")
        print(f"  Categories          : {fm['category'].value_counts().to_dict()}")
        if "sub_category" in fm.columns:
            print(f"  Sub-categories      : {fm['sub_category'].nunique()}")
        if "risk_category" in fm.columns:
            print(f"  Risk grades         : {fm['risk_category'].value_counts().to_dict()}")

    print(f"\n  ✓ Ingestion complete. {len(loaded)}/{len(DATASETS)} datasets loaded.")
    print("  Next step → run scripts/live_nav_fetch.py\n")


if __name__ == "__main__":
    main()
