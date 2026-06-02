"""
live_nav_fetch.py
Bluestock Fintech | Mutual Fund Analytics Capstone
Day 1: Fetch live historical NAV from mfapi.in for 5 selected schemes.

Usage:
    python scripts/live_nav_fetch.py
"""

import time
import requests
import pandas as pd
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── Schemes to fetch ─────────────────────────────────────────────────────────
# (amfi_code, fund_house, scheme_name)
SCHEMES = [
    (125497, "HDFC MF",       "HDFC Top 100 Fund - Direct Plan"),
    (119551, "SBI MF",        "SBI Bluechip Fund - Direct Plan"),
    (120503, "ICICI Pru MF",  "ICICI Prudential Bluechip Fund - Direct Plan"),
    (118632, "Nippon MF",     "Nippon India Large Cap Fund - Direct Plan"),
    (119092, "Axis MF",       "Axis Bluechip Fund - Direct Plan"),
]

BASE_URL = "https://api.mfapi.in/mf/{code}"


def fetch_nav(amfi_code: int, scheme_name: str) -> pd.DataFrame | None:
    """
    Fetch full NAV history for a scheme from mfapi.in.

    Returns a DataFrame with columns: amfi_code, date, nav, scheme_name
    """
    url = BASE_URL.format(code=amfi_code)
    print(f"\n  Fetching: {scheme_name} (code={amfi_code})")
    print(f"  URL     : {url}")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        payload = response.json()

        if "data" not in payload or not payload["data"]:
            print("  ⚠ No NAV data returned.")
            return None

        df = pd.DataFrame(payload["data"])           # columns: date, nav
        df["amfi_code"]   = amfi_code
        df["scheme_name"] = scheme_name

        # Normalise columns
        df.rename(columns={"date": "nav_date"}, inplace=True)
        df["nav_date"] = pd.to_datetime(df["nav_date"], format="%d-%m-%Y", errors="coerce")
        df["nav"]      = pd.to_numeric(df["nav"], errors="coerce")
        df.dropna(subset=["nav_date", "nav"], inplace=True)
        df.sort_values("nav_date", inplace=True)
        df.reset_index(drop=True, inplace=True)

        print(f"  ✓ {len(df):,} records | NAV range: {df['nav'].min():.2f} – {df['nav'].max():.2f}")
        print(f"    Date range: {df['nav_date'].min().date()} → {df['nav_date'].max().date()}")
        return df[["amfi_code", "scheme_name", "nav_date", "nav"]]

    except requests.exceptions.Timeout:
        print("  ✗ Request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Request failed: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    return None


def main() -> None:
    print("\n" + "█"*60)
    print("  BLUESTOCK FINTECH — Day 1: Live NAV Fetch (mfapi.in)")
    print("█"*60)

    all_frames = []

    for amfi_code, fund_house, scheme_name in SCHEMES:
        df = fetch_nav(amfi_code, scheme_name)
        if df is not None:
            # Save individual file
            fname = RAW_DIR / f"nav_live_{amfi_code}.csv"
            df.to_csv(fname, index=False)
            print(f"  Saved → {fname.name}")
            all_frames.append(df)
        time.sleep(0.5)   # polite delay between API calls

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        out_path = RAW_DIR / "nav_live_combined.csv"
        combined.to_csv(out_path, index=False)
        print(f"\n  ✓ Combined file saved → {out_path.name}")
        print(f"    Total records: {len(combined):,} across {combined['amfi_code'].nunique()} schemes")

        # Spot-check: HDFC Top 100 anchor value (Oct 2024 ≈ Rs. 892.45)
        hdfc = combined[combined["amfi_code"] == 125497].copy()
        oct24 = hdfc[hdfc["nav_date"].dt.to_period("M") == "2024-10"]
        if not oct24.empty:
            print(f"\n  Anchor check — HDFC Top 100, Oct 2024:")
            print(f"    Min NAV: {oct24['nav'].min():.2f}  Max NAV: {oct24['nav'].max():.2f}")
            print(f"    (Expected ≈ Rs. 892.45 per AMFI)")
    else:
        print("\n  ✗ No data fetched. Check your internet connection.")

    print("\n  Next step → python scripts/etl_pipeline.py\n")


if __name__ == "__main__":
    main()
