"""
run_pipeline.py
Bluestock Fintech | Mutual Fund Analytics Capstone
Day 7: Master execution script — runs the complete pipeline end to end.

Usage:
    python scripts/run_pipeline.py              # Full pipeline
    python scripts/run_pipeline.py --step etl   # Single step only

Steps:
    ingest   → Load & validate all 10 CSVs
    nav      → Fetch live NAV from mfapi.in
    etl      → Clean all datasets + load into SQLite
    queries  → Run 10 analytical SQL queries
    eda      → Generate 15 EDA charts
    advanced → VaR, CVaR, Cohort, HHI, Recommender
"""

import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DB_PATH     = BASE_DIR / "data" / "db" / "bluestock_mf.db"
RAW_DIR     = BASE_DIR / "data" / "raw"

# ── Pipeline steps in order ───────────────────────────────────────────────────
STEPS = [
    ("ingest",   "data_ingestion.py",      "Day 1 — Data Ingestion (all 10 CSVs)"),
    ("nav",      "live_nav_fetch.py",       "Day 1 — Live NAV Fetch (mfapi.in)"),
    ("etl",      "etl_pipeline.py",         "Day 2 — ETL: Clean + Load SQLite DB"),
    ("queries",  "run_queries.py",           "Day 2 — Run 10 SQL Analytical Queries"),
    ("eda",      "eda_analysis.py",          "Day 3 — EDA Analysis (15 charts)"),
    ("advanced", "advanced_analytics.py",   "Day 6 — Advanced Analytics + Risk Metrics"),
]


def banner(text: str, char: str = "=") -> None:
    width = 62
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def run_step(script_name: str, label: str) -> bool:
    """
    Run a single pipeline script as a subprocess.
    Returns True if successful, False if it failed.
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"  SKIP — {script_name} not found at {script_path}")
        return True  # Non-fatal — script may not be present

    banner(label, "-")
    start = time.time()
    print(f"  Running: python scripts/{script_name}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}\n")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(BASE_DIR),
        capture_output=False,
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n  DONE in {elapsed:.1f}s")
        return True
    else:
        print(f"\n  FAILED (exit code {result.returncode}) after {elapsed:.1f}s")
        print(f"  Fix the error above and re-run: python scripts/{script_name}")
        return False


def preflight_check() -> bool:
    """
    Check prerequisites before running the pipeline.
    Returns True if all checks pass.
    """
    banner("Pre-flight Checks")
    ok = True

    # Check data/raw/ has at least some CSVs
    csv_files = list(RAW_DIR.glob("*.csv")) if RAW_DIR.exists() else []
    if not csv_files:
        print(f"  FAIL — No CSV files found in data/raw/")
        print(f"         Place the 10 Bluestock datasets in data/raw/ and re-run.")
        ok = False
    else:
        print(f"  OK   — {len(csv_files)} CSV file(s) found in data/raw/")

    # Check required scripts exist
    required_scripts = ["etl_pipeline.py", "eda_analysis.py", "advanced_analytics.py"]
    for s in required_scripts:
        path = SCRIPTS_DIR / s
        if path.exists():
            print(f"  OK   — scripts/{s} found")
        else:
            print(f"  WARN — scripts/{s} not found (step will be skipped)")

    # Check Python packages
    required_packages = ["pandas","numpy","matplotlib","seaborn","sqlalchemy","requests","scipy"]
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"\n  FAIL — Missing packages: {', '.join(missing)}")
        print(f"         Run: pip install {' '.join(missing)}")
        ok = False
    else:
        print(f"  OK   — All required Python packages are installed")

    return ok


def print_summary(results: dict, total_time: float) -> None:
    """Print a final summary table of all pipeline steps."""
    banner("Pipeline Summary")
    print(f"  {'Step':<12} {'Script':<35} {'Status'}")
    print(f"  {'-'*12} {'-'*35} {'-'*8}")
    for key, label, script, status in results:
        icon = "PASS" if status else "FAIL"
        print(f"  {key:<12} {script:<35} {icon}")

    passed = sum(1 for _, _, _, s in results if s)
    failed = len(results) - passed
    print(f"\n  Total: {passed}/{len(results)} steps passed | "
          f"Time: {total_time:.1f}s ({total_time/60:.1f} min)")

    if failed == 0:
        print("\n  ALL STEPS COMPLETE!")
        print(f"  Database : data/db/bluestock_mf.db")
        print(f"  Charts   : reports/charts/ (15–21 PNGs)")
        print(f"  Next     : Open dashboard/bluestock_mf.pbix in Power BI")
    else:
        print(f"\n  {failed} step(s) failed. Fix errors above and re-run.")


def main():
    parser = argparse.ArgumentParser(
        description="Bluestock MF Capstone — Master Pipeline Runner"
    )
    parser.add_argument(
        "--step",
        choices=[s[0] for s in STEPS],
        help="Run only a single pipeline step (default: run all)"
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip pre-flight checks"
    )
    args = parser.parse_args()

    banner("BLUESTOCK FINTECH — Mutual Fund Analytics Pipeline", "=")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Base dir: {BASE_DIR}")

    # Pre-flight
    if not args.skip_preflight:
        if not preflight_check():
            print("\n  Pre-flight checks failed. Fix issues above and retry.")
            sys.exit(1)

    pipeline_start = time.time()
    results = []

    if args.step:
        # Single step mode
        step = next(s for s in STEPS if s[0] == args.step)
        key, script, label = step
        status = run_step(script, label)
        results.append((key, label, script, status))
    else:
        # Full pipeline
        for key, script, label in STEPS:
            status = run_step(script, label)
            results.append((key, label, script, status))
            if not status:
                print("\n  Pipeline halted due to error.")
                print(f"  To resume from this step: python scripts/run_pipeline.py --step {key}")
                break

    total_time = time.time() - pipeline_start
    print_summary(results, total_time)


if __name__ == "__main__":
    main()
