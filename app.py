import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics",
    page_icon="📈",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "processed"

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    data = {}

    files = [
        "clean_aum_by_fund_house.csv",
        "clean_monthly_sip_inflows.csv",
        "clean_scheme_performance.csv",
        "clean_investor_transactions.csv",
        "clean_category_inflows.csv",
        "clean_benchmark_indices.csv",
        "clean_fund_master.csv"
    ]

    for f in files:
        path = DATA_DIR / f
        if path.exists():
            data[f] = pd.read_csv(path)

    return data

data = load_data()

st.title("📊 Bluestock Mutual Fund Analytics Dashboard")

page = st.sidebar.selectbox(
    "Select Page",
    [
        "Industry Overview",
        "Fund Performance",
        "Investor Analytics",
        "SIP & Market Trends"
    ]
)

# ====================================================
# PAGE 1
# ====================================================

if page == "Industry Overview":

    st.header("Industry Overview")

    aum = data["clean_aum_by_fund_house.csv"]
    sip = data["clean_monthly_sip_inflows.csv"]
    funds = data["clean_fund_master.csv"]

    total_aum = aum["aum_crore"].sum()
    total_sip = sip["sip_inflow_crore"].sum()
    total_schemes = len(funds)

    c1, c2, c3 = st.columns(3)

    c1.metric("Total AUM", f"₹{total_aum:,.0f} Cr")
    c2.metric("Total SIP", f"₹{total_sip:,.0f} Cr")
    c3.metric("Schemes", total_schemes)

    st.subheader("AUM by AMC")

    top_aum = (
        aum.groupby("fund_house")["aum_crore"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_aum,
        x="fund_house",
        y="aum_crore",
        color="aum_crore"
    )

    st.plotly_chart(fig, use_container_width=True)

# ====================================================
# PAGE 2
# ====================================================

elif page == "Fund Performance":

    st.header("Fund Performance")

    perf = data["clean_scheme_performance.csv"]

    fig = px.scatter(
        perf,
        x="std_dev_ann_pct",
        y="return_3yr_pct",
        size="aum_crore",
        color="category",
        hover_name="scheme_name"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Sharpe Ratio Funds")

    top_sharpe = (
        perf.sort_values("sharpe_ratio", ascending=False)
        .head(10)
    )

    st.dataframe(
        top_sharpe[
            [
                "scheme_name",
                "sharpe_ratio",
                "alpha",
                "beta"
            ]
        ]
    )

# ====================================================
# PAGE 3
# ====================================================

elif page == "Investor Analytics":

    st.header("Investor Analytics")

    tx = data["clean_investor_transactions.csv"]

    state_data = (
        tx.groupby("state")["amount_inr"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        state_data,
        x="state",
        y="amount_inr"
    )

    st.plotly_chart(fig, use_container_width=True)

    split = (
        tx.groupby("transaction_type")["amount_inr"]
        .sum()
        .reset_index()
    )

    fig2 = px.pie(
        split,
        names="transaction_type",
        values="amount_inr",
        hole=0.5
    )

    st.plotly_chart(fig2, use_container_width=True)

# ====================================================
# PAGE 4
# ====================================================

elif page == "SIP & Market Trends":

    st.header("SIP & Market Trends")

    sip = data["clean_monthly_sip_inflows.csv"]

    fig = px.line(
        sip,
        x="month",
        y="sip_inflow_crore",
        title="Monthly SIP Inflow"
    )

    st.plotly_chart(fig, use_container_width=True)

    cat = data["clean_category_inflows.csv"]

    top_cat = (
        cat.groupby("category")["net_inflow_crore"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    fig2 = px.bar(
        top_cat,
        x="category",
        y="net_inflow_crore"
    )

    st.plotly_chart(fig2, use_container_width=True)