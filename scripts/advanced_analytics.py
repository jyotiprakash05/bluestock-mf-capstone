"""
advanced_analytics.py
Bluestock Fintech | Mutual Fund Analytics Capstone
Day 6: Advanced Analytics + Risk Metrics

Covers:
  1. Historical VaR (95%) and CVaR per fund
  2. Rolling 90-day Sharpe Ratio (5 funds)
  3. Investor Cohort Analysis
  4. SIP Continuation / At-Risk Investors
  5. Sector Concentration (HHI Index)
  6. Fund Recommendation Engine

Usage:
    python scripts/advanced_analytics.py
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Paths
BASE_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = BASE_DIR / "data" / "processed"
CHARTS_DIR = BASE_DIR / "reports" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Style
plt.rcParams.update({
    "figure.facecolor" : "#0d1117",
    "axes.facecolor"   : "#161b22",
    "axes.edgecolor"   : "#30363d",
    "axes.labelcolor"  : "#c9d1d9",
    "axes.titlecolor"  : "#f0f6fc",
    "xtick.color"      : "#8b949e",
    "ytick.color"      : "#8b949e",
    "text.color"       : "#c9d1d9",
    "grid.color"       : "#21262d",
    "grid.linestyle"   : "--",
    "grid.alpha"       : 0.5,
    "legend.facecolor" : "#161b22",
    "legend.edgecolor" : "#30363d",
    "font.size"        : 10,
})

COLORS = ["#58a6ff","#3fb950","#f78166","#d2a8ff","#ffa657",
          "#79c0ff","#56d364","#ff7b72","#bc8cff","#ffb86c"]


def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


def save_chart(name):
    path = CHARTS_DIR / f"{name}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=plt.rcParams["figure.facecolor"])
    plt.close()
    print(f"  Saved -> reports/charts/{name}.png")


def load_csv(name):
    path = PROC_DIR / f"clean_{name}.csv"
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    print(f"  WARNING: clean_{name}.csv not found in data/processed/")
    return pd.DataFrame()


def save_result(df, name):
    path = PROC_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  Saved -> data/processed/{name}.csv  ({len(df):,} rows)")


# =============================================================================
# 1. VALUE AT RISK (VaR) & CONDITIONAL VaR
# =============================================================================
def compute_var_cvar():
    """
    Historical VaR and CVaR at 95% confidence level.

    VaR  = 5th percentile of daily return distribution
           Meaning: on 95% of days, loss will NOT exceed this value

    CVaR = Mean of all returns below the VaR threshold
           Meaning: on the worst 5% of days, average loss is CVaR
    """
    section("1. Computing VaR & CVaR (95% Confidence)")

    nav   = load_csv("nav_history")
    funds = load_csv("fund_master")
    if nav.empty:
        return pd.DataFrame()

    nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
    nav["amfi_code"] = nav["amfi_code"].astype(str)
    nav = nav[nav["date"] >= "2022-01-01"].copy()
    nav["daily_return_pct"] = pd.to_numeric(nav["daily_return_pct"], errors="coerce")

    results = []
    for code, grp in nav.groupby("amfi_code"):
        returns = grp["daily_return_pct"].dropna()
        if len(returns) < 100:
            continue
        var_95  = float(np.percentile(returns, 5))
        cvar_95 = float(returns[returns <= var_95].mean())
        results.append({
            "amfi_code"       : code,
            "var_95_pct"      : round(var_95  * 100, 4),
            "cvar_95_pct"     : round(cvar_95 * 100, 4),
            "daily_std_pct"   : round(float(returns.std()) * 100, 4),
            "skewness"        : round(float(returns.skew()), 4),
            "kurtosis"        : round(float(returns.kurt()), 4),
            "num_trading_days": len(returns),
        })

    df_var = pd.DataFrame(results)
    if df_var.empty:
        print("  No VaR results computed.")
        return df_var

    if not funds.empty:
        funds["amfi_code"] = funds["amfi_code"].astype(str)
        df_var = df_var.merge(
            funds[["amfi_code","scheme_name","category","fund_house"]],
            on="amfi_code", how="left")

    df_var.sort_values("var_95_pct", inplace=True)
    save_result(df_var, "var_cvar_report")

    name_col = "scheme_name" if "scheme_name" in df_var.columns else "amfi_code"
    risk_cols = [c for c in [name_col, "category", "var_95_pct", "cvar_95_pct"]
                 if c in df_var.columns]

    print("\n  Top 5 RISKIEST funds (worst VaR):")
    print(df_var[risk_cols].head(5).to_string(index=False))
    print("\n  Top 5 SAFEST funds (best VaR):")
    print(df_var[risk_cols].tail(5).to_string(index=False))

    # Chart
    plot_df = df_var.copy()
    plot_df["short_name"] = plot_df[name_col].astype(str).str.split(" - ").str[0].str[:28]

    fig, ax = plt.subplots(figsize=(13, 8))
    bar_colors = ["#f78166" if v < -1.5 else "#ffa657" if v < -1.0 else "#3fb950"
                  for v in plot_df["var_95_pct"]]
    bars = ax.barh(plot_df["short_name"], plot_df["var_95_pct"],
                   color=bar_colors, edgecolor="#0d1117", alpha=0.85)
    ax.axvline(-1.0, color="#ffa657", linewidth=1.2, linestyle="--", label="VaR = -1% (caution)")
    ax.axvline(-1.5, color="#f78166", linewidth=1.2, linestyle="--", label="VaR = -1.5% (high risk)")
    ax.axvline(0,    color="#8b949e", linewidth=0.8)
    for bar, val in zip(bars, plot_df["var_95_pct"]):
        ax.text(val - 0.05, bar.get_y() + bar.get_height()/2,
                f"{val:.2f}%", va="center", ha="right", fontsize=7)
    ax.set_title("Historical VaR (95%) by Fund", fontsize=14, pad=15)
    ax.set_xlabel("VaR (% daily loss at 95% confidence)")
    ax.legend(fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    save_chart("16_var_95_by_fund")

    return df_var


# =============================================================================
# 2. ROLLING 90-DAY SHARPE RATIO
# =============================================================================
def compute_rolling_sharpe():
    """
    Rolling 90-day Sharpe Ratio shows how risk-adjusted returns change over time.
    A falling Sharpe means the fund is becoming less efficient per unit of risk.
    """
    section("2. Rolling 90-Day Sharpe Ratio")

    nav   = load_csv("nav_history")
    funds = load_csv("fund_master")
    if nav.empty:
        return

    nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
    nav["amfi_code"] = nav["amfi_code"].astype(str)
    nav["daily_return_pct"] = pd.to_numeric(nav["daily_return_pct"], errors="coerce")
    nav = nav[nav["date"] >= "2022-01-01"].copy()

    top5 = nav.groupby("amfi_code")["date"].count().nlargest(5).index.tolist()

    name_map = {}
    if not funds.empty:
        funds["amfi_code"] = funds["amfi_code"].astype(str)
        name_map = dict(zip(funds["amfi_code"],
                            funds["scheme_name"].str.split(" - ").str[0].str[:25]))

    rf_daily = 0.065 / 252

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, code in enumerate(top5):
        grp = nav[nav["amfi_code"] == code].set_index("date").sort_index()
        returns = grp["daily_return_pct"].dropna()
        roll_mean   = returns.rolling(90).mean()
        roll_std    = returns.rolling(90).std()
        roll_sharpe = ((roll_mean - rf_daily) / roll_std) * np.sqrt(252)
        roll_sharpe = roll_sharpe.replace([np.inf, -np.inf], np.nan)
        label = name_map.get(code, code)
        ax.plot(roll_sharpe.index, roll_sharpe.values,
                color=COLORS[i], linewidth=1.8, label=label, alpha=0.9)

    ax.axhline(0,    color="#8b949e", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhline(1.0,  color="#3fb950", linewidth=1.0, linestyle="--", alpha=0.7, label="Sharpe=1.0 (good)")
    ax.axhline(-1.0, color="#f78166", linewidth=1.0, linestyle="--", alpha=0.7, label="Sharpe=-1.0 (poor)")
    ax.set_title("Rolling 90-Day Sharpe Ratio — Top 5 Funds (2022–2026)", fontsize=14, pad=15)
    ax.set_xlabel("Date")
    ax.set_ylabel("Sharpe Ratio (annualised)")
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_chart("17_rolling_sharpe_ratio")
    print("  Rolling Sharpe chart saved.")


# =============================================================================
# 3. INVESTOR COHORT ANALYSIS
# =============================================================================
def investor_cohort_analysis():
    """
    Group investors by the year of their first transaction.
    Compare behaviour: avg SIP, total invested, number of investors.
    """
    section("3. Investor Cohort Analysis")

    tx = load_csv("investor_transactions")
    if tx.empty:
        return pd.DataFrame()

    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"], errors="coerce")
    tx["amount_inr"] = pd.to_numeric(tx["amount_inr"], errors="coerce")

    first_tx = (tx.groupby("investor_id")["transaction_date"]
                  .min().dt.year.rename("cohort_year"))
    tx = tx.merge(first_tx, on="investor_id", how="left")

    cohort = (tx[tx["transaction_type"] == "SIP"]
              .groupby("cohort_year")
              .agg(
                  num_investors    = ("investor_id", "nunique"),
                  avg_sip_amount   = ("amount_inr", "mean"),
                  total_invested   = ("amount_inr", "sum"),
                  num_transactions = ("amount_inr", "count"),
              ).reset_index())
    cohort["avg_sip_amount"] = cohort["avg_sip_amount"].round(0)
    cohort["total_invested"] = (cohort["total_invested"] / 1e7).round(2)

    print("\n  Cohort Summary:")
    print(cohort.to_string(index=False))
    save_result(cohort, "cohort_analysis")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Investor Cohort Analysis", fontsize=14)

    axes[0].bar(cohort["cohort_year"].astype(str), cohort["avg_sip_amount"],
                color=COLORS[:len(cohort)], edgecolor="#0d1117", alpha=0.85)
    axes[0].set_title("Avg SIP Amount by Cohort Year")
    axes[0].set_xlabel("First Investment Year")
    axes[0].set_ylabel("Avg SIP Amount (Rs.)")
    for bar, val in zip(axes[0].patches, cohort["avg_sip_amount"]):
        axes[0].text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 50,
                     f"Rs.{val:,.0f}", ha="center", fontsize=9)

    axes[1].bar(cohort["cohort_year"].astype(str), cohort["num_investors"],
                color=COLORS[1:len(cohort)+1], edgecolor="#0d1117", alpha=0.85)
    axes[1].set_title("Number of Investors by Cohort Year")
    axes[1].set_xlabel("First Investment Year")
    axes[1].set_ylabel("Number of Investors")

    plt.tight_layout()
    save_chart("18_cohort_analysis")
    return cohort


# =============================================================================
# 4. SIP CONTINUATION ANALYSIS
# =============================================================================
def sip_continuation_analysis():
    """
    For investors with 6+ SIP transactions:
    Compute avg gap between SIPs.
    Flag as at-risk if avg gap > 35 days.
    """
    section("4. SIP Continuation Analysis")

    tx = load_csv("investor_transactions")
    if tx.empty:
        return pd.DataFrame()

    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"], errors="coerce")
    sip_tx = tx[tx["transaction_type"] == "SIP"].copy()
    sip_tx.sort_values(["investor_id","transaction_date"], inplace=True)
    sip_tx["prev_date"] = sip_tx.groupby("investor_id")["transaction_date"].shift(1)
    sip_tx["gap_days"]  = (sip_tx["transaction_date"] - sip_tx["prev_date"]).dt.days

    sip_counts = sip_tx.groupby("investor_id")["transaction_date"].count()
    active     = sip_counts[sip_counts >= 6].index
    sip_active = sip_tx[sip_tx["investor_id"].isin(active)].copy()

    continuity = (sip_active.groupby("investor_id")
                  .agg(
                      num_sips       = ("transaction_date", "count"),
                      avg_gap_days   = ("gap_days", "mean"),
                      max_gap_days   = ("gap_days", "max"),
                      total_invested = ("amount_inr", "sum"),
                  ).reset_index())
    continuity["avg_gap_days"]   = continuity["avg_gap_days"].round(1)
    continuity["max_gap_days"]   = continuity["max_gap_days"].fillna(0).astype(int)
    continuity["at_risk"]        = continuity["avg_gap_days"] > 35
    continuity["total_invested"] = continuity["total_invested"].round(0)

    at_risk_count = int(continuity["at_risk"].sum())
    active_count  = len(continuity)
    at_risk_pct   = round(at_risk_count / active_count * 100, 1) if active_count > 0 else 0

    print(f"\n  Active SIP investors (6+ SIPs) : {active_count:,}")
    print(f"  At-risk (avg gap > 35 days)    : {at_risk_count:,} ({at_risk_pct}%)")
    print(f"  Overall avg gap                : {continuity['avg_gap_days'].mean():.1f} days")
    save_result(continuity, "sip_continuity")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("SIP Continuation Analysis", fontsize=14)

    axes[0].hist(continuity["avg_gap_days"].dropna(), bins=30,
                 color=COLORS[0], edgecolor="#0d1117", alpha=0.85)
    axes[0].axvline(35, color="#f78166", linewidth=2, linestyle="--",
                    label="At-risk threshold (35 days)")
    axes[0].set_title("Distribution of Avg SIP Gap (Days)")
    axes[0].set_xlabel("Avg Days Between SIPs")
    axes[0].set_ylabel("Number of Investors")
    axes[0].legend(fontsize=9)

    axes[1].pie(
        [active_count - at_risk_count, at_risk_count],
        labels=["Regular SIP", f"At-Risk ({at_risk_pct}%)"],
        autopct="%1.1f%%",
        colors=[COLORS[1], COLORS[2]],
        startangle=90,
        wedgeprops={"edgecolor":"#0d1117","linewidth":1.5})
    axes[1].set_title("SIP Continuity Status")

    plt.tight_layout()
    save_chart("19_sip_continuity")
    return continuity


# =============================================================================
# 5. SECTOR CONCENTRATION — HHI INDEX
# =============================================================================
def sector_hhi_analysis():
    """
    HHI = sum(sector_weight_i ^ 2)
    Range: 0 to 10000
      > 2500 = Highly concentrated (risky)
      1500-2500 = Moderately concentrated
      < 1500 = Well diversified
    """
    section("5. Sector Concentration (HHI Index)")

    port  = load_csv("portfolio_holdings")
    funds = load_csv("fund_master")
    if port.empty:
        return pd.DataFrame()

    port["amfi_code"]  = port["amfi_code"].astype(str)
    port["weight_pct"] = pd.to_numeric(port["weight_pct"], errors="coerce").fillna(0)

    sector_wts = port.groupby(["amfi_code","sector"])["weight_pct"].sum().reset_index()

    hhi_results = []
    for code, grp in sector_wts.groupby("amfi_code"):
        weights    = grp["weight_pct"].values
        hhi        = float(np.sum(weights ** 2))
        top_sector = grp.loc[grp["weight_pct"].idxmax(), "sector"] if not grp.empty else "N/A"
        top_wt     = float(grp["weight_pct"].max())

        if hhi > 2500:
            level = "High"
        elif hhi > 1500:
            level = "Moderate"
        else:
            level = "Diversified"

        hhi_results.append({
            "amfi_code"    : code,
            "hhi_score"    : round(hhi, 2),
            "concentration": level,
            "top_sector"   : top_sector,
            "top_sector_wt": round(top_wt, 2),
            "num_sectors"  : len(grp),
        })

    df_hhi = pd.DataFrame(hhi_results)
    if df_hhi.empty:
        print("  No HHI results computed.")
        return df_hhi

    if not funds.empty:
        funds["amfi_code"] = funds["amfi_code"].astype(str)
        df_hhi = df_hhi.merge(
            funds[["amfi_code","scheme_name","category"]],
            on="amfi_code", how="left")

    df_hhi.sort_values("hhi_score", ascending=False, inplace=True)
    save_result(df_hhi, "sector_hhi")

    print("\n  Concentration levels:")
    print(df_hhi["concentration"].value_counts().to_string())
    cols = [c for c in ["scheme_name","hhi_score","concentration","top_sector"]
            if c in df_hhi.columns]
    print("\n  Most concentrated funds (top 5):")
    print(df_hhi[cols].head(5).to_string(index=False))

    # Chart
    name_col = "scheme_name" if "scheme_name" in df_hhi.columns else "amfi_code"
    plot_df  = df_hhi.copy()
    plot_df["short_name"] = plot_df[name_col].astype(str).str.split(" - ").str[0].str[:28]

    color_map = {"High":"#f78166","Moderate":"#ffa657","Diversified":"#3fb950"}
    bar_colors = [color_map.get(c, "#58a6ff") for c in plot_df["concentration"]]

    fig, ax = plt.subplots(figsize=(13, 8))
    ax.barh(plot_df["short_name"], plot_df["hhi_score"],
            color=bar_colors, edgecolor="#0d1117", alpha=0.85)
    ax.axvline(2500, color="#f78166", linewidth=1.5, linestyle="--", label="HHI=2500 (High)")
    ax.axvline(1500, color="#ffa657", linewidth=1.5, linestyle="--", label="HHI=1500 (Moderate)")

    legend_elements = [
        mpatches.Patch(facecolor="#f78166", label="High"),
        mpatches.Patch(facecolor="#ffa657", label="Moderate"),
        mpatches.Patch(facecolor="#3fb950", label="Diversified"),
    ]
    ax.legend(handles=legend_elements, fontsize=9, title="Concentration")
    ax.set_title("Sector Concentration (HHI) by Fund", fontsize=14, pad=15)
    ax.set_xlabel("HHI Score (higher = more concentrated)")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    save_chart("20_sector_hhi")

    return df_hhi


# =============================================================================
# 6. FUND RECOMMENDATION ENGINE
# =============================================================================
def fund_recommender():
    """
    Rule-based recommendation engine.
    Maps investor risk appetite to SEBI risk categories,
    then returns top 3 funds by Sharpe ratio.
    """
    section("6. Fund Recommendation Engine")

    perf  = load_csv("scheme_performance")
    funds = load_csv("fund_master")
    if perf.empty or funds.empty:
        print("  WARNING: Data not available"); return

    perf["amfi_code"]  = perf["amfi_code"].astype(str)
    funds["amfi_code"] = funds["amfi_code"].astype(str)

    # Only pick fund columns that actually exist, rename to avoid merge suffix conflicts
    want = ["amfi_code","scheme_name","fund_house","category","risk_category","expense_ratio_pct"]
    avail = [c for c in want if c in funds.columns]
    funds_slim = funds[avail].copy()
    # Prefix non-key columns so they never clash with perf columns
    funds_slim.rename(columns={c: f"f_{c}" for c in avail if c != "amfi_code"}, inplace=True)

    merged = perf.merge(funds_slim, on="amfi_code", how="left")
    merged["sharpe_ratio"] = pd.to_numeric(merged["sharpe_ratio"], errors="coerce")

    # Resolve actual column names after merge
    scheme_col = next((c for c in ["f_scheme_name","scheme_name"] if c in merged.columns), None)
    house_col  = next((c for c in ["f_fund_house","fund_house"]   if c in merged.columns), None)
    cat_col    = next((c for c in ["f_category","category"]       if c in merged.columns), None)
    risk_col   = next((c for c in ["f_risk_category","risk_category"] if c in merged.columns), None)
    exp_col    = next((c for c in ["f_expense_ratio_pct","expense_ratio_pct"] if c in merged.columns), None)

    risk_map = {
        "Low"     : ["Low","Moderately Low"],
        "Moderate": ["Moderate","Moderately High"],
        "High"    : ["High","Very High"],
    }
    cat_fallback = {
        "Low"     : ["Debt"],
        "Moderate": ["Hybrid"],
        "High"    : ["Equity"],
    }

    def recommend(appetite, top_n=3):
        allowed = risk_map.get(appetite, [])
        if risk_col and merged[risk_col].notna().any():
            f = merged[merged[risk_col].isin(allowed)]
        elif cat_col:
            f = merged[merged[cat_col].isin(cat_fallback.get(appetite, []))]
        else:
            f = merged.copy()
        if f.empty:
            f = merged.copy()
        # Build output column list from only existing columns
        out_cols = ["amfi_code"] + [c for c in
                    [scheme_col, house_col, cat_col, "sharpe_ratio", "return_3yr_pct", exp_col]
                    if c and c in f.columns]
        return f.nlargest(top_n, "sharpe_ratio")[out_cols].reset_index(drop=True)

    print("\n" + "-"*58)
    for appetite in ["Low","Moderate","High"]:
        recs = recommend(appetite)
        print(f"\n  Top 3 funds for {appetite.upper()} risk appetite:")
        print(f"  {'Fund':<35} {'Sharpe':>8} {'3yr%':>8} {'Exp%':>6}")
        print(f"  {'-'*35} {'-'*8} {'-'*8} {'-'*6}")
        for _, row in recs.iterrows():
            name   = str(row.get(scheme_col or "amfi_code","N/A")).split(" - ")[0][:34]
            sharpe = f"{row['sharpe_ratio']:.2f}" if pd.notna(row.get("sharpe_ratio")) else "N/A"
            ret3   = f"{row['return_3yr_pct']:.1f}%" if pd.notna(row.get("return_3yr_pct")) else "N/A"
            exp_v  = row.get(exp_col) if exp_col else None
            exp    = f"{exp_v:.2f}%" if exp_col and pd.notna(exp_v) else "N/A"
            print(f"  {name:<35} {sharpe:>8} {ret3:>8} {exp:>6}")
    print("-"*58)

    # Chart
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle("Fund Recommendations by Risk Appetite", fontsize=14)
    for i, appetite in enumerate(["Low","Moderate","High"]):
        recs = recommend(appetite)
        if recs.empty:
            continue
        name_c = scheme_col if scheme_col and scheme_col in recs.columns else recs.columns[1]
        recs["short_name"] = recs[name_c].astype(str).str.split(" - ").str[0].str[:20]
        axes[i].barh(recs["short_name"], recs["sharpe_ratio"],
                     color=COLORS[i*2:i*2+3], edgecolor="#0d1117", alpha=0.85)
        axes[i].set_title(f"{appetite} Risk", fontsize=12)
        axes[i].set_xlabel("Sharpe Ratio")
        axes[i].axvline(1.0, color="#ffa657", linewidth=1, linestyle="--", alpha=0.7)
        axes[i].grid(axis="x", alpha=0.3)
    plt.tight_layout()
    save_chart("21_fund_recommendations")


# =============================================================================
# SUMMARY
# =============================================================================
def print_advanced_summary(df_var, df_hhi, cohort, continuity):
    section("Advanced Analytics — Key Insights")
    insights = []

    if not df_var.empty and "var_95_pct" in df_var.columns:
        name_col = "scheme_name" if "scheme_name" in df_var.columns else "amfi_code"
        riskiest = df_var.iloc[0]
        safest   = df_var.iloc[-1]
        insights.append(
            f"1. HIGHEST RISK  : {str(riskiest.get(name_col,'N/A')).split(' - ')[0][:30]} "
            f"VaR={riskiest['var_95_pct']:.2f}% | CVaR={riskiest['cvar_95_pct']:.2f}%")
        insights.append(
            f"2. LOWEST RISK   : {str(safest.get(name_col,'N/A')).split(' - ')[0][:30]} "
            f"VaR={safest['var_95_pct']:.2f}% | CVaR={safest['cvar_95_pct']:.2f}%")

    if not df_hhi.empty and "concentration" in df_hhi.columns:
        high_n = (df_hhi["concentration"] == "High").sum()
        insights.append(f"3. CONCENTRATION : {high_n} funds have HIGH sector concentration (HHI > 2500)")

    if not cohort.empty and "avg_sip_amount" in cohort.columns:
        best = cohort.loc[cohort["avg_sip_amount"].idxmax()]
        insights.append(
            f"4. BEST COHORT   : {int(best['cohort_year'])} cohort — avg SIP = Rs.{best['avg_sip_amount']:,.0f}")

    if not continuity.empty and "at_risk" in continuity.columns:
        pct = continuity["at_risk"].mean() * 100
        insights.append(f"5. SIP AT-RISK   : {pct:.1f}% of active investors show irregular SIP patterns")

    for ins in insights:
        print(f"  {ins}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("\n" + "="*60)
    print("  BLUESTOCK FINTECH -- Day 6: Advanced Analytics")
    print("="*60)

    df_var     = compute_var_cvar()
    compute_rolling_sharpe()
    cohort     = investor_cohort_analysis()
    continuity = sip_continuation_analysis()
    df_hhi     = sector_hhi_analysis()
    fund_recommender()

    print_advanced_summary(df_var, df_hhi, cohort, continuity)

    section("Day 6 Complete")
    print("  CSV outputs -> data/processed/")
    print("    var_cvar_report.csv")
    print("    cohort_analysis.csv")
    print("    sip_continuity.csv")
    print("    sector_hhi.csv")
    print("  Charts -> reports/charts/ (charts 16-21)")
    print("  Next step -> Day 7: Final Report + Presentation")


if __name__ == "__main__":
    main()
