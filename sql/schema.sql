-- ============================================================
-- schema.sql
-- Bluestock Fintech | Mutual Fund Analytics Capstone
-- 5-table Star Schema for SQLite / PostgreSQL
-- ============================================================

-- ── DIMENSION: Fund Master ───────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code         TEXT PRIMARY KEY,
    fund_house        TEXT NOT NULL,
    scheme_name       TEXT NOT NULL,
    category          TEXT,          -- Equity / Debt / Hybrid
    sub_category      TEXT,          -- Large Cap / Mid Cap / etc.
    plan              TEXT,          -- Direct / Regular
    benchmark         TEXT,
    expense_ratio_pct REAL,
    exit_load_pct     REAL,
    fund_manager      TEXT,
    risk_category     TEXT,          -- Low / Moderate / High / Very High
    launch_date       DATE,
    sebi_category_code TEXT
);

-- ── DIMENSION: Date ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_date (
    date_id    INTEGER PRIMARY KEY,  -- YYYYMMDD integer key
    date       DATE    NOT NULL UNIQUE,
    year       INTEGER,
    month      INTEGER,
    quarter    INTEGER,
    month_name TEXT,
    is_weekday INTEGER              -- 1 = Mon-Fri, 0 = Sat/Sun
);

-- ── FACT: Daily NAV ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_nav (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code        TEXT    NOT NULL REFERENCES dim_fund(amfi_code),
    nav_date         DATE    NOT NULL,
    nav              REAL    NOT NULL,
    daily_return_pct REAL,           -- (NAV_t / NAV_t-1) - 1
    UNIQUE (amfi_code, nav_date)
);
CREATE INDEX IF NOT EXISTS idx_nav_code_date ON fact_nav (amfi_code, nav_date);

-- ── FACT: Investor Transactions ─────────────────────────────
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id              TEXT PRIMARY KEY,
    investor_id        TEXT    NOT NULL,
    amfi_code          TEXT    NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_date   DATE    NOT NULL,
    transaction_type   TEXT    NOT NULL, -- SIP / Lumpsum / Redemption
    amount_inr         INTEGER NOT NULL,
    state              TEXT,
    city               TEXT,
    city_tier          TEXT,            -- T30 / B30
    age_group          TEXT,
    gender             TEXT,
    annual_income_lakh REAL,
    payment_mode       TEXT,
    kyc_status         TEXT
);
CREATE INDEX IF NOT EXISTS idx_tx_investor ON fact_transactions (investor_id);
CREATE INDEX IF NOT EXISTS idx_tx_code     ON fact_transactions (amfi_code);

-- ── FACT: Scheme Performance ─────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code          TEXT NOT NULL REFERENCES dim_fund(amfi_code),
    as_of_date         DATE NOT NULL,
    return_1yr_pct     REAL,
    return_3yr_pct     REAL,
    return_5yr_pct     REAL,
    benchmark_3yr_pct  REAL,
    alpha              REAL,
    beta               REAL,
    sharpe_ratio       REAL,
    sortino_ratio      REAL,
    std_dev_ann_pct    REAL,
    max_drawdown_pct   REAL,
    morningstar_rating INTEGER,
    PRIMARY KEY (amfi_code, as_of_date)
);

-- ── FACT: Portfolio Holdings ─────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_portfolio (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code    TEXT  NOT NULL REFERENCES dim_fund(amfi_code),
    as_of_date   DATE  NOT NULL,
    stock_symbol TEXT,
    stock_name   TEXT,
    sector       TEXT,
    weight_pct   REAL,
    UNIQUE (amfi_code, as_of_date, stock_symbol)
);

-- ── FACT: AUM by Fund House ──────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_aum (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house  TEXT NOT NULL,
    quarter     TEXT NOT NULL,          -- e.g. 'Q3-FY25'
    date        DATE NOT NULL,
    aum_crore   REAL NOT NULL,
    num_schemes INTEGER,
    UNIQUE (fund_house, date)
);

-- ── FACT: Monthly SIP Industry Data ─────────────────────────
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    month                   TEXT NOT NULL UNIQUE,  -- YYYY-MM
    sip_inflow_crore        REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh   REAL,
    sip_aum_lakh_crore      REAL,
    yoy_growth_pct          REAL
);
