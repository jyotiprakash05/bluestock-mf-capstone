-- ============================================================
-- queries.sql
-- Bluestock Fintech | Mutual Fund Analytics Capstone
-- 10 Analytical SQL Queries (Day 2)
-- Run against: bluestock_mf.db
-- ============================================================

-- ── Q1: Top 5 fund houses by latest AUM ─────────────────────
SELECT
    fund_house,
    ROUND(MAX(aum_crore), 2) AS latest_aum_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY latest_aum_crore DESC
LIMIT 5;

-- ── Q2: Average NAV per month for a given fund ──────────────
-- (Replace '125497' with any amfi_code)
SELECT
    STRFTIME('%Y-%m', nav_date)  AS month,
    ROUND(AVG(nav), 2)           AS avg_nav,
    ROUND(MIN(nav), 2)           AS min_nav,
    ROUND(MAX(nav), 2)           AS max_nav
FROM fact_nav
WHERE amfi_code = '125497'
GROUP BY month
ORDER BY month;

-- ── Q3: SIP inflow YoY growth ────────────────────────────────
SELECT
    SUBSTR(month, 1, 4)          AS year,
    ROUND(SUM(sip_inflow_crore), 2) AS total_sip_crore,
    ROUND(AVG(yoy_growth_pct), 2)   AS avg_yoy_growth_pct
FROM fact_sip_industry
GROUP BY year
ORDER BY year;

-- ── Q4: Transaction amount by state ──────────────────────────
SELECT
    state,
    COUNT(*)                           AS num_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)   AS total_amount_crore,
    ROUND(AVG(amount_inr), 0)          AS avg_transaction_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_crore DESC;

-- ── Q5: Funds with expense ratio < 1% ────────────────────────
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.expense_ratio_pct
FROM dim_fund f
WHERE f.expense_ratio_pct < 1.0
ORDER BY f.expense_ratio_pct;

-- ── Q6: Best performing funds by 3-year CAGR ─────────────────
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.alpha
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 10;

-- ── Q7: SIP vs Lumpsum vs Redemption split ───────────────────
SELECT
    transaction_type,
    COUNT(*)                           AS count,
    ROUND(SUM(amount_inr) / 1e7, 2)   AS total_crore,
    ROUND(AVG(amount_inr), 0)          AS avg_amount_inr
FROM fact_transactions
GROUP BY transaction_type;

-- ── Q8: Investor demographics — avg SIP by age group ─────────
SELECT
    age_group,
    COUNT(DISTINCT investor_id)       AS num_investors,
    ROUND(AVG(amount_inr), 0)         AS avg_amount_inr,
    ROUND(SUM(amount_inr) / 1e7, 2)  AS total_invested_crore
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY age_group;

-- ── Q9: Top equity holdings by weight across all funds ───────
SELECT
    stock_name,
    sector,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct,
    COUNT(DISTINCT amfi_code) AS num_funds_holding
FROM fact_portfolio
GROUP BY stock_name, sector
ORDER BY avg_weight_pct DESC
LIMIT 15;

-- ── Q10: T30 vs B30 city tier contribution ───────────────────
SELECT
    city_tier,
    COUNT(*)                           AS num_transactions,
    COUNT(DISTINCT investor_id)        AS unique_investors,
    ROUND(SUM(amount_inr) / 1e7, 2)   AS total_amount_crore,
    ROUND(100.0 * SUM(amount_inr) /
          (SELECT SUM(amount_inr) FROM fact_transactions), 2) AS pct_share
FROM fact_transactions
GROUP BY city_tier;
