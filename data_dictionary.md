# Data Dictionary
## Bluestock Fintech — Mutual Fund Analytics Capstone

All datasets are sourced from publicly available AMFI India data, mfapi.in, and simulated investor data
with real geographic and demographic distributions.

---

## 01 — dim_fund (fund_master)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| amfi_code | TEXT (PK) | AMFI unique scheme code | 125497 |
| fund_house | TEXT | AMC / fund house name | HDFC Mutual Fund |
| scheme_name | TEXT | Full official AMFI scheme name | HDFC Top 100 Fund - Direct Plan |
| category | TEXT | Broad category | Equity / Debt / Hybrid |
| sub_category | TEXT | SEBI sub-category | Large Cap / Mid Cap / Small Cap |
| plan | TEXT | Plan type | Direct / Regular |
| benchmark | TEXT | Official benchmark index | Nifty 100 TRI |
| expense_ratio_pct | REAL | Annual expense ratio % | 0.57 |
| exit_load_pct | REAL | Exit load % | 1.0 |
| fund_manager | TEXT | Primary fund manager name | Rahul Baijal |
| risk_category | TEXT | SEBI risk grade | Low / Moderate / High / Very High |
| launch_date | DATE | Fund launch date | 2013-01-01 |
| sebi_category_code | TEXT | Internal SEBI code | EC01 = LargeCap |

---

## 02 — fact_nav (nav_history)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| amfi_code | TEXT (FK) | Foreign key to dim_fund | 125497 |
| date | DATE | NAV date (business days only) | 2024-10-15 |
| nav | REAL | NAV in Rs. | 892.4560 |
| daily_return_pct | REAL | (NAV_t / NAV_t-1) - 1 | 0.00123 |

**Note:** NAV values are anchored to real AMFI data. Missing dates (weekends/holidays) are forward-filled.

---

## 03 — fact_aum (aum_by_fund_house)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| fund_house | TEXT | AMC name | SBI Mutual Fund |
| quarter | TEXT | Quarter label | Q3-FY25 |
| date | DATE | Quarter end date | 2024-12-31 |
| aum_crore | REAL | AUM in Rs. crore | 1250000.00 |
| num_schemes | INTEGER | Number of schemes managed | 42 |

**Key values:** SBI MF = Rs. 12.5 lakh crore, ICICI Pru = Rs. 10.74 lakh crore (Dec 2025)

---

## 04 — fact_sip_industry (monthly_sip_inflows)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| month | TEXT | YYYY-MM format | 2025-12 |
| sip_inflow_crore | REAL | Total SIP inflows in Rs. crore | 31002.00 |
| active_sip_accounts_crore | REAL | Active SIP accounts in crore | 9.35 |
| new_sip_accounts_lakh | REAL | New SIP registrations (lakh) | 49.23 |
| sip_aum_lakh_crore | REAL | SIP AUM in Rs. lakh crore | 13.48 |
| yoy_growth_pct | REAL | YoY growth % in SIP inflows | 18.5 |

**Milestone:** Dec 2025 SIP inflow = Rs. 31,002 crore (all-time high)

---

## 05 — fact_category_inflows (category_inflows)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| month | TEXT | YYYY-MM | 2025-03 |
| category | TEXT | Fund category | Large Cap |
| net_inflow_crore | REAL | Net inflow in Rs. crore | 2341.50 |

---

## 06 — fact_folio_count (industry_folio_count)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date | DATE | Record date | 2025-12-31 |
| equity_folios_crore | REAL | Equity fund folios in crore | 14.82 |
| debt_folios_crore | REAL | Debt fund folios in crore | 4.31 |
| hybrid_folios_crore | REAL | Hybrid fund folios in crore | 6.99 |
| total_folios_crore | REAL | Total folios in crore | 26.12 |

---

## 07 — fact_performance (scheme_performance)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| amfi_code | TEXT (FK) | Foreign key to dim_fund | 125497 |
| return_1yr_pct | REAL | 1-year absolute return % | 18.42 |
| return_3yr_pct | REAL | 3-year CAGR % | 14.87 |
| return_5yr_pct | REAL | 5-year CAGR % | 16.23 |
| benchmark_3yr_pct | REAL | Benchmark 3yr CAGR % | 13.50 |
| alpha | REAL | Excess return over benchmark | 1.37 |
| beta | REAL | Market sensitivity (1.0 = market) | 0.95 |
| sharpe_ratio | REAL | Risk-adjusted return (>1 is good) | 1.23 |
| sortino_ratio | REAL | Downside-only risk-adjusted return | 1.45 |
| std_dev_ann_pct | REAL | Annualised std dev of daily returns % | 14.2 |
| max_drawdown_pct | REAL | Worst peak-to-trough decline % | -28.4 |
| morningstar_rating | INTEGER | 1–5 star rating | 4 |

---

## 08 — fact_transactions (investor_transactions)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| investor_id | TEXT | Unique investor ID | INV000001 |
| transaction_date | DATE | Date of transaction | 2024-06-15 |
| amfi_code | TEXT (FK) | Fund invested in | 125497 |
| transaction_type | TEXT | SIP / Lumpsum / Redemption | SIP |
| amount_inr | INTEGER | Transaction amount in Rs. | 5000 |
| state | TEXT | Investor's state | Maharashtra |
| city | TEXT | Investor's city | Mumbai |
| city_tier | TEXT | T30 = Top 30 cities, B30 = Beyond Top 30 | T30 |
| age_group | TEXT | Investor age bracket | 26-35 |
| gender | TEXT | Male / Female | Male |
| annual_income_lakh | REAL | Annual income in Rs. lakh | 12.5 |
| payment_mode | TEXT | UPI / Net Banking / Mandate / Cheque | UPI |
| kyc_status | TEXT | Verified (92%) / Pending (8%) | Verified |

---

## 09 — fact_portfolio (portfolio_holdings)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| amfi_code | TEXT (FK) | Foreign key to dim_fund | 125497 |
| as_of_date | DATE | Holdings as of date | 2025-12-31 |
| stock_symbol | TEXT | NSE/BSE stock symbol | RELIANCE |
| stock_name | TEXT | Full company name | Reliance Industries Ltd |
| sector | TEXT | Industry sector | Energy |
| weight_pct | REAL | Portfolio weight % | 8.42 |

---

## 10 — fact_benchmark (benchmark_indices)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date | DATE | Trading date | 2024-10-15 |
| nifty_50 | REAL | Nifty 50 closing value | 24964.25 |
| nifty_100 | REAL | Nifty 100 closing value | 25318.40 |
| nifty_midcap_150 | REAL | Nifty Midcap 150 value | 18742.10 |
| bse_smallcap | REAL | BSE SmallCap index value | 52341.75 |
| crisil_liquid | REAL | CRISIL Liquid index value | 3124.50 |
| crisil_gilt | REAL | CRISIL Gilt index value | 2841.30 |

---

## Important Units Reference

| Metric | Unit | Watch out for |
|--------|------|--------------|
| AUM (scheme level) | Rs. crore | Don't confuse with lakh crore |
| AUM (industry level) | Rs. lakh crore | 1 lakh crore = 100 crore × 100 |
| SIP inflow | Rs. crore | Monthly figure |
| NAV | Rs. per unit | Single fund unit price |
| Returns | % | Already in percentage form |
| Expense ratio | % per annum | Range: 0.1% – 2.5% |
| Folio count | crore | Number of investor accounts |
