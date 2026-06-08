# compute_metrics.py
"""
compute_metrics.py
Bluestock Fintech Capstone
Day 4 - Fund Performance Analytics
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROC_DIR = BASE_DIR / "data" / "processed"

REPORT_DIR = BASE_DIR / "reports" / "metrics"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CHART_DIR = BASE_DIR / "reports" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# STYLE
# =====================================================

plt.style.use("dark_background")

BLUESTOCK_BLUE = "#58a6ff"

# =====================================================
# LOAD DATA
# =====================================================

print("\nLoading Scheme Performance Data...")

scheme_file = PROC_DIR / "clean_scheme_performance.csv"

if not scheme_file.exists():
    raise FileNotFoundError(
        f"\nFile not found:\n{scheme_file}"
    )

df = pd.read_csv(scheme_file)

print(f"Rows Loaded    : {len(df)}")
print(f"Columns Loaded : {len(df.columns)}")

print("\nAvailable Columns:")
print(df.columns.tolist())

# =====================================================
# IDENTIFY NAME COLUMN
# =====================================================

name_col = None

for col in df.columns:

    if col.lower() in [
        "scheme_name",
        "fund_name",
        "scheme",
        "fund",
        "name"
    ]:
        name_col = col
        break

if name_col is None:

    for col in df.columns:
        if "scheme" in col.lower():
            name_col = col
            break

if name_col is None:
    name_col = "amfi_code"

print(f"\nUsing Name Column : {name_col}")

# =====================================================
# REQUIRED COLUMNS CHECK
# =====================================================

required_cols = [
    "return_3yr_pct",
    "alpha",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "std_dev_ann_pct",
    "max_drawdown_pct"
]

missing = [
    c for c in required_cols
    if c not in df.columns
]

if missing:

    print("\nMissing Columns:")
    print(missing)

    raise Exception(
        "Required columns not found."
    )

# =====================================================
# CLEAN NUMERIC DATA
# =====================================================

numeric_cols = [
    "return_3yr_pct",
    "alpha",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "std_dev_ann_pct",
    "max_drawdown_pct"
]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df.dropna(
    subset=["return_3yr_pct"],
    inplace=True
)

# =====================================================
# COMPOSITE SCORECARD
# =====================================================

print("\nComputing Composite Score...")

df["return_rank"] = (
    df["return_3yr_pct"]
    .rank(ascending=False)
)

df["sharpe_rank"] = (
    df["sharpe_ratio"]
    .rank(ascending=False)
)

df["alpha_rank"] = (
    df["alpha"]
    .rank(ascending=False)
)

df["drawdown_rank"] = (
    df["max_drawdown_pct"]
    .rank(ascending=True)
)

df["composite_score"] = (
      df["return_rank"] * 0.30
    + df["sharpe_rank"] * 0.25
    + df["alpha_rank"] * 0.20
    + df["drawdown_rank"] * 0.10
)

scorecard = (
    df.sort_values(
        "composite_score"
    )
)

scorecard.to_csv(
    REPORT_DIR / "fund_scorecard.csv",
    index=False
)

print("Saved -> fund_scorecard.csv")

# =====================================================
# TOP ALPHA
# =====================================================

top_alpha = (
    df.sort_values(
        "alpha",
        ascending=False
    )
    .head(10)
)

top_alpha.to_csv(
    REPORT_DIR / "top_alpha.csv",
    index=False
)

print("Saved -> top_alpha.csv")

# =====================================================
# TOP BETA
# =====================================================

top_beta = (
    df.sort_values(
        "beta",
        ascending=False
    )
    .head(10)
)

top_beta.to_csv(
    REPORT_DIR / "top_beta.csv",
    index=False
)

print("Saved -> top_beta.csv")

# =====================================================
# BEST BY CATEGORY
# =====================================================

if "category" in df.columns:

    best_by_category = (
        df.groupby("category")
        .apply(
            lambda x:
            x.nsmallest(
                3,
                "composite_score"
            )
        )
        .reset_index(drop=True)
    )

    best_by_category.to_csv(
        REPORT_DIR /
        "best_by_category.csv",
        index=False
    )

    print("Saved -> best_by_category.csv")

# =====================================================
# CHART 1
# SHARPE RANKING
# =====================================================

top_sharpe = (
    df.sort_values(
        "sharpe_ratio",
        ascending=False
    )
    .head(10)
)

plt.figure(figsize=(12,6))

plt.barh(
    top_sharpe[name_col].astype(str),
    top_sharpe["sharpe_ratio"],
    color=BLUESTOCK_BLUE
)

plt.title(
    "Top 10 Funds by Sharpe Ratio"
)

plt.xlabel(
    "Sharpe Ratio"
)

plt.tight_layout()

plt.savefig(
    CHART_DIR /
    "sharpe_ranking.png",
    dpi=300
)

plt.close()

print("Saved -> sharpe_ranking.png")

# =====================================================
# CHART 2
# RISK VS RETURN
# =====================================================

plt.figure(figsize=(12,7))

sns.scatterplot(
    data=df,
    x="std_dev_ann_pct",
    y="return_3yr_pct",
    s=80
)

plt.title(
    "Risk vs Return"
)

plt.xlabel(
    "Annualized Risk (%)"
)

plt.ylabel(
    "3-Year Return (%)"
)

plt.tight_layout()

plt.savefig(
    CHART_DIR /
    "risk_return_scatter.png",
    dpi=300
)

plt.close()

print("Saved -> risk_return_scatter.png")

# =====================================================
# CHART 3
# ALPHA VS BETA
# =====================================================

plt.figure(figsize=(12,7))

sns.scatterplot(
    data=df,
    x="beta",
    y="alpha",
    s=80
)

plt.title(
    "Alpha vs Beta"
)

plt.xlabel("Beta")
plt.ylabel("Alpha")

plt.tight_layout()

plt.savefig(
    CHART_DIR /
    "alpha_beta_scatter.png",
    dpi=300
)

plt.close()

print("Saved -> alpha_beta_scatter.png")

# =====================================================
# SUMMARY
# =====================================================

print("\n" + "="*60)
print("DAY 4 ANALYTICS COMPLETE")
print("="*60)

print("\nGenerated Metrics:")
print("fund_scorecard.csv")
print("top_alpha.csv")
print("top_beta.csv")

print("\nGenerated Charts:")
print("sharpe_ranking.png")
print("risk_return_scatter.png")
print("alpha_beta_scatter.png")

print("\nOutput Folders:")
print("reports/metrics/")
print("reports/charts/")
