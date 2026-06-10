# 📊 Bluestock Fintech — Mutual Fund Analytics Capstone

> **End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard**
> Built by [Jyoti Prakash](https://github.com/jyotiprakash05) | Bluestock Fintech Pvt. Ltd. | June 2026

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green?logo=pandas)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?logo=sqlite)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi)
![License](https://img.shields.io/badge/License-Educational-orange)

---

## 🎯 Project Overview

This capstone project builds a full-stack **Mutual Fund Analytics Platform** for Bluestock Fintech that:

- Ingests **40 real mutual fund schemes** from AMFI India & mfapi.in
- Processes **87,000+ rows** across 10 datasets spanning 4.5 years (Jan 2022 – May 2026)
- Stores data in a **normalised SQLite star schema** database
- Computes **risk-adjusted return metrics** (Sharpe, Sortino, Alpha, Beta, VaR)
- Presents insights via a **4-page interactive Power BI dashboard**

---

## 📁 Project Structure

```
bluestock-mf-capstone/
├── data/
│   ├── raw/                    ← 10 source CSVs + 5 live NAV files from mfapi.in
│   ├── processed/              ← 10 cleaned CSVs + computed metrics
│   └── db/                     ← bluestock_mf.db (SQLite) — gitignored
│
├── scripts/
│   ├── data_ingestion.py       ← Day 1: Load & validate all 10 datasets
│   ├── live_nav_fetch.py       ← Day 1: Fetch live NAV from mfapi.in API
│   ├── etl_pipeline.py         ← Day 2: Clean data + load into SQLite
│   ├── run_queries.py          ← Day 2: Run 10 analytical SQL queries
│   ├── eda_analysis.py         ← Day 3: 15+ EDA charts (Matplotlib/Seaborn)
│   ├── advanced_analytics.py   ← Day 6: VaR, CVaR, Cohort, HHI, Recommender
│   ├── dashboard_app.py        ← Day 5: Dashboard using Power BI
│   └── run_pipeline.py         ← Master script — runs full pipeline end to end
│
├── sql/
│   ├── schema.sql              ← Star schema: 8 CREATE TABLE statements
│   └── queries.sql             ← 10 analytical SQL queries
│
├── dashboard/
│   └── bluestock_mf.pbix       ← Power BI dashboard (4 pages)
│
├── reports/
│   ├── Final_Report.md         ← Complete project report
│   └── charts/                 ← 21 exported chart PNGs
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/jyotiprakash05/bluestock-mf-capstone.git
cd bluestock-mf-capstone
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Place the 10 datasets in `data/raw/`
```
data/raw/01_fund_master.csv
data/raw/02_nav_history.csv
data/raw/03_aum_by_fund_house.csv
data/raw/04_monthly_sip_inflows.csv
data/raw/05_category_inflows.csv
data/raw/06_industry_folio_count.csv
data/raw/07_scheme_performance.csv
data/raw/08_investor_transactions.csv
data/raw/09_portfolio_holdings.csv
data/raw/10_benchmark_indices.csv
```

### 4. Run the full pipeline (one command)
```bash
python scripts/run_pipeline.py
```

Or run day by day:
```bash
python scripts/data_ingestion.py      # Day 1: Ingest
python scripts/live_nav_fetch.py      # Day 1: Live NAV
python scripts/etl_pipeline.py        # Day 2: Clean + DB
python scripts/run_queries.py         # Day 2: SQL queries
python scripts/eda_analysis.py        # Day 3: EDA charts
python scripts/advanced_analytics.py  # Day 6: Advanced metrics
```

### 5. Open the dashboard
Open `dashboard/bluestock_mf.pbix` in **Power BI Desktop**

---

## 📦 Datasets

| # | File | Rows | Description |
|---|------|------|-------------|
| 01 | `fund_master.csv` | 40 | Master info for 40 real AMFI schemes |
| 02 | `nav_history.csv` | ~46,000 | Daily NAV Jan 2022 – May 2026 |
| 03 | `aum_by_fund_house.csv` | ~90 | Quarterly AUM for 10 fund houses |
| 04 | `monthly_sip_inflows.csv` | 48 | Industry SIP inflow data |
| 05 | `category_inflows.csv` | ~144 | Net inflows by fund category |
| 06 | `industry_folio_count.csv` | 21 | Total MF folios (crore) |
| 07 | `scheme_performance.csv` | 40 | Risk & return metrics per fund |
| 08 | `investor_transactions.csv` | ~32,000 | SIP/Lumpsum/Redemption transactions |
| 09 | `portfolio_holdings.csv` | ~320 | Top equity holdings per fund |
| 10 | `benchmark_indices.csv` | ~8,000 | Nifty 50, 100, BSE SmallCap daily values |

---

## 🗄️ Database Schema (Star Schema)

```
                    dim_fund (centre)
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
   fact_nav    fact_transactions    fact_performance
        │                                  │
   fact_benchmark              fact_portfolio
        │
   fact_aum + fact_sip_industry
```

| Table | Type | Rows |
|-------|------|------|
| `dim_fund` | Dimension | 40 |
| `fact_nav` | Fact | ~46,000 |
| `fact_transactions` | Fact | ~32,000 |
| `fact_performance` | Fact | 40 |
| `fact_portfolio` | Fact | ~320 |
| `fact_aum` | Fact | ~90 |
| `fact_sip_industry` | Fact | 48 |
| `fact_benchmark` | Fact | ~8,000 |

---

## 📈 Key Metrics Computed

| Metric | Formula | Purpose |
|--------|---------|---------|
| **CAGR** | `(NAV_end/NAV_start)^(1/n) - 1` | Annualised return |
| **Sharpe Ratio** | `(Rp - Rf) / Std(Rp) × √252` | Risk-adjusted return |
| **Sortino Ratio** | `(Rp - Rf) / Downside_Std × √252` | Penalises only downside |
| **Alpha** | `OLS intercept × 252` | Excess return vs benchmark |
| **Beta** | `OLS slope` | Market sensitivity |
| **Max Drawdown** | `min(NAV / running_max - 1)` | Worst peak-to-trough loss |
| **VaR (95%)** | `5th percentile of daily returns` | Daily loss threshold |
| **CVaR (95%)** | `Mean of returns below VaR` | Expected loss on worst days |
| **HHI** | `Σ(sector_weight²)` | Portfolio concentration |

---

## 📊 Dashboard Pages (Power BI)

| Page | Contents |
|------|----------|
| **1. Industry Overview** | KPI cards (AUM ₹81L Cr, SIP ₹31K Cr, Folios 26.12 Cr), AUM trend, AUM by AMC |
| **2. Fund Performance** | Risk vs Return scatter, Sharpe ranking, NAV vs Benchmark, Fund scorecard |
| **3. Investor Analytics** | State investment, SIP/Lumpsum/Redemption split, Age group, T30 vs B30 |
| **4. SIP & Market Trends** | SIP inflow vs Nifty 50 dual-axis, Category inflow heatmap, Top categories |

---

## 🔬 Advanced Analytics (Day 6)

| Analysis | Output |
|---------|--------|
| Historical VaR & CVaR (95%) | `var_cvar_report.csv` |
| Rolling 90-Day Sharpe Ratio | `charts/17_rolling_sharpe_ratio.png` |
| Investor Cohort Analysis | `cohort_analysis.csv` |
| SIP Continuation / At-Risk | `sip_continuity.csv` |
| Sector HHI Concentration | `sector_hhi.csv` |
| Fund Recommendation Engine | Low / Moderate / High risk output |

---

## 🛠️ Tech Stack

| Category | Tool | Version |
|---------|------|---------|
| Language | Python | 3.13 |
| Data Processing | Pandas, NumPy | 2.x, 1.24+ |
| Visualisation | Matplotlib, Seaborn, Plotly | 3.7+, 0.12+, 5.x |
| Database | SQLite3 + SQLAlchemy | Built-in, 2.0 |
| Statistics | SciPy | 1.10+ |
| Dashboard | Power BI Desktop | Latest |
| API | mfapi.in | v1 (no auth) |
| Version Control | Git + GitHub | Latest |

---

## 📋 Data Sources

| Source | URL | Data |
|--------|-----|------|
| AMFI India | amfiindia.com | NAV, AUM, SIP, Folio data |
| mfapi.in | api.mfapi.in/mf/{code} | Historical NAV (JSON, free) |
| NSE India | nseindia.com | Nifty 50, Nifty 100 |
| BSE India | bseindia.com | BSE SmallCap index |

---

## ✅ Objectives Completed

| # | Objective | Status |
|---|-----------|--------|
| O1 | ETL pipeline from raw AMFI data | ✅ `etl_pipeline.py` |
| O2 | Normalised SQL schema (star schema) | ✅ `schema.sql` — 8 tables |
| O3 | EDA on NAV & AUM data | ✅ 15 charts in `eda_analysis.py` |
| O4 | Performance & risk metrics per scheme | ✅ Sharpe, Alpha, Beta, VaR |
| O5 | Interactive BI dashboard | ✅ `bluestock_mf.pbix` — 4 pages |
| O6 | Investor transaction pattern analysis | ✅ Cohort + SIP continuity |
| O7 | Fund returns vs benchmark indices | ✅ Alpha, tracking error |
| O8 | Documentation and presentation | ✅ README + Final Report |

---

## ⚠️ Disclaimer

All data is sourced from publicly available AMFI India data, mfapi.in, and NSE/BSE.
Investor transaction data is synthetically generated with real demographic distributions.
This project is for **educational purposes only** and does not constitute financial advice.
Mutual Fund investments are subject to market risks.

---

*Built as part of the Bluestock Fintech Data Analyst Internship Capstone — June 2026*
