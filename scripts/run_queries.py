"""
run_queries.py
Bluestock Fintech | Mutual Fund Analytics Capstone
Day 2: Run all 10 analytical SQL queries against bluestock_mf.db

Usage:
    python scripts/run_queries.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "data" / "db" / "bluestock_mf.db"

if not DB_PATH.exists():
    print("✗ Database not found. Run etl_pipeline.py first.")
    exit(1)

# ── Queries ───────────────────────────────────────────────────────────────────
QUERIES = {
    "Q1 — Top 5 Fund Houses by AUM": """
        SELECT fund_house,
               ROUND(MAX(aum_crore), 2) AS latest_aum_crore
        FROM fact_aum
        GROUP BY fund_house
        ORDER BY latest_aum_crore DESC
        LIMIT 5
    """,

    "Q2 — Avg Monthly NAV for HDFC Top 100 (last 12 months)": """
        SELECT STRFTIME('%Y-%m', date) AS month,
               ROUND(AVG(nav), 2)      AS avg_nav,
               ROUND(MIN(nav), 2)      AS min_nav,
               ROUND(MAX(nav), 2)      AS max_nav
        FROM fact_nav
        WHERE amfi_code = '125497'
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """,

    "Q3 — SIP Inflow by Year": """
        SELECT SUBSTR(month, 1, 4)             AS year,
               ROUND(SUM(sip_inflow_crore), 2) AS total_sip_crore
        FROM fact_sip_industry
        GROUP BY year
        ORDER BY year
    """,

    "Q4 — Transaction Amount by State (Top 10)": """
        SELECT state,
               COUNT(*)                          AS num_transactions,
               ROUND(SUM(amount_inr)/1e7, 2)    AS total_crore,
               ROUND(AVG(amount_inr), 0)         AS avg_amount_inr
        FROM fact_transactions
        GROUP BY state
        ORDER BY total_crore DESC
        LIMIT 10
    """,

    "Q5 — Funds with Expense Ratio < 1%": """
        SELECT amfi_code, scheme_name, fund_house,
               category, expense_ratio_pct
        FROM dim_fund
        WHERE expense_ratio_pct < 1.0
        ORDER BY expense_ratio_pct
    """,

    "Q6 — Top 10 Funds by 3-Year CAGR": """
        SELECT f.scheme_name, f.fund_house, f.category,
               p.return_3yr_pct, p.sharpe_ratio, p.alpha
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.return_3yr_pct DESC
        LIMIT 10
    """,

    "Q7 — SIP vs Lumpsum vs Redemption Split": """
        SELECT transaction_type,
               COUNT(*)                         AS count,
               ROUND(SUM(amount_inr)/1e7, 2)   AS total_crore,
               ROUND(AVG(amount_inr), 0)        AS avg_amount_inr
        FROM fact_transactions
        GROUP BY transaction_type
    """,

    "Q8 — Avg SIP Amount by Age Group": """
        SELECT age_group,
               COUNT(DISTINCT investor_id)      AS num_investors,
               ROUND(AVG(amount_inr), 0)        AS avg_amount_inr,
               ROUND(SUM(amount_inr)/1e7, 2)   AS total_invested_crore
        FROM fact_transactions
        WHERE transaction_type = 'SIP'
        GROUP BY age_group
        ORDER BY age_group
    """,

    "Q9 — Top 15 Stock Holdings Across Funds": """
        SELECT stock_name, sector,
               ROUND(AVG(weight_pct), 2)    AS avg_weight_pct,
               COUNT(DISTINCT amfi_code)    AS num_funds_holding
        FROM fact_portfolio
        GROUP BY stock_name, sector
        ORDER BY avg_weight_pct DESC
        LIMIT 15
    """,

    "Q10 — T30 vs B30 City Tier Contribution": """
        SELECT city_tier,
               COUNT(*)                          AS num_transactions,
               COUNT(DISTINCT investor_id)       AS unique_investors,
               ROUND(SUM(amount_inr)/1e7, 2)    AS total_amount_crore,
               ROUND(100.0 * SUM(amount_inr) /
                    (SELECT SUM(amount_inr) FROM fact_transactions), 2
               ) AS pct_share
        FROM fact_transactions
        GROUP BY city_tier
    """,
}


def run_all_queries() -> None:
    print("\n" + "█"*60)
    print("  BLUESTOCK FINTECH — Day 2: SQL Query Results")
    print("█"*60)

    with sqlite3.connect(DB_PATH) as conn:
        for title, sql in QUERIES.items():
            print(f"\n{'─'*60}")
            print(f"  {title}")
            print(f"{'─'*60}")
            try:
                df = pd.read_sql_query(sql.strip(), conn)
                if df.empty:
                    print("  (no results — table may be empty)")
                else:
                    print(df.to_string(index=False))
            except Exception as e:
                print(f"  ✗ Error: {e}")

    print(f"\n{'='*60}")
    print("  ✓ All queries complete!")
    print("  Next step → Day 3: EDA Analysis")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_all_queries()
