"""Veltrix customer segments: a read-only summary app.

Shows the eight segments (model seg-v1.0), how they behave, the planned campaign test and the monitoring.
It reads only aggregate files from app/data/ (see prepare_app_data.py). It holds no customer-level data.
The data is synthetic: Veltrix is a fictional estate agency.
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Veltrix customer segments",
                   page_icon=":house:", layout="wide")
DATA = Path(__file__).parent / "data"

DESCRIPTIONS = {   # provisional: written from the notebook 06/07 profiles. Update if the model is rebuilt.
    "Downsizers": "Chain-free buyers, mostly retired, who prefer phone and branch over mobile. Bungalows, mid-to-high budgets.",
    "Home movers": "Families buying semis and detached homes, often in a chain. The highest purchase budgets of the main buyer groups.",
    "Window shoppers": "Heavy browsers who rarely enquire. Most never state a budget and most have no lead.",
    "First-time buyers": "The largest segment. Lower budgets, mostly on mobile, mostly mortgage-funded, slowest to decide.",
    "Buy-to-let investors": "Portfolio landlords, often buying through a company. Lowest budgets per property, quick to decide.",
    "Overseas investors": "Living abroad, buying new-build and off-plan, often browsing at night (UK time).",
    "Corporate relocation lets": "Company lets. A small group with the highest monthly rents and the highest conversion.",
    "Young renters": "Renting at roughly the market average, almost all on mobile, deciding within about two weeks.",
}


@st.cache_data
def load_csv(name, **kw):
    p = DATA / name
    return pd.read_csv(p, **kw) if p.exists() else None


@st.cache_data
def load_text(name):
    p = DATA / name
    return p.read_text(encoding="utf-8") if p.exists() else None


stats = load_csv("segment_statistics.csv", index_col=0)
if stats is None:
    st.error(
        "No data found in app/data/. From the repo root run:  python app/prepare_app_data.py")
    st.stop()

stats = stats.rename(columns=lambda c: c.strip())
num_cols = [c for c in stats.columns if c not in (
    "segment", "top_regions", "top_lead_sources")]
for c in num_cols:
    stats[c] = pd.to_numeric(stats[c], errors="coerce")


def bar(df, col, title, fmt=",.1f", color="#1f4e79"):
    d = df[["segment", col]].dropna()
    return (alt.Chart(d, title=title).mark_bar(color=color)
            .encode(x=alt.X(f"{col}:Q", title=None), y=alt.Y("segment:N", sort="-x", title=None),
                    tooltip=["segment", alt.Tooltip(f"{col}:Q", format=fmt)])
            .properties(height=max(180, 32 * len(d))))


st.title("Veltrix customer segments")
st.caption("Model seg-v1.0 | synthetic data (Veltrix is a fictional agency) | names are provisional and being confirmed with the DA team")

tab_over, tab_seg, tab_out, tab_test, tab_mon, tab_about = st.tabs(
    ["Overview", "Segment profiles", "Outcomes", "Campaign test", "Monitoring", "About the model"])

with tab_over:
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", f"{int(stats['customers'].sum()):,}")
    c2.metric("Segments", len(stats))
    biggest = stats["customers"].idxmax()
    c3.metric("Largest segment",
              f"{stats.loc[biggest, 'segment']} ({stats.loc[biggest, 'share_%']:.0f}%)")
    st.altair_chart(
        bar(stats, "share_%", "Share of customers (%)"), width="stretch")
    show = [c for c in ["segment", "customers", "share_%", "median_budget_gbp",
                        "conversion_%", "median_days_to_decision"] if c in stats.columns]
    st.dataframe(stats[show].sort_values(
        "customers", ascending=False), width="stretch", hide_index=True)
    st.caption("Budgets: purchase budgets are in GBP, renter budgets are per month. Conversion is the share of customers with at least one lead who converted.")

with tab_seg:
    names = stats["segment"].tolist()
    choice = st.selectbox("Segment", names)
    r = stats[stats["segment"] == choice].iloc[0]
    st.subheader(choice)
    if choice in DESCRIPTIONS:
        st.write(DESCRIPTIONS[choice])
    m = st.columns(4)
    m[0].metric("Share of customers", f"{r['share_%']:.1f}%")
    m[1].metric("Median budget", f"£{r['median_budget_gbp']:,.0f}")
    m[2].metric("Conversion", f"{r['conversion_%']:.1f}%")
    m[3].metric("Median days to decide", f"{r['median_days_to_decision']:.0f}")
    if "top_regions" in stats.columns:
        st.write("**Where they live:** " + str(r["top_regions"]))
        st.write("**How they find us:** " + str(r["top_lead_sources"]))
    cmp = stats.copy()
    cmp["selected"] = cmp["segment"].eq(choice)
    ch = (alt.Chart(cmp, title="Conversion (%): selected segment highlighted").mark_bar()
          .encode(x=alt.X("conversion_%:Q", title=None), y=alt.Y("segment:N", sort="-x", title=None),
                  color=alt.condition("datum.selected", alt.value(
                      "#d62728"), alt.value("#9db7d1")),
                  tooltip=["segment", "conversion_%"]).properties(height=260))
    st.altair_chart(ch, width="stretch")

with tab_out:
    st.write("What happened to customers after they enquired. These measures were **not** used to build the segments.")
    a, b = st.columns(2)
    a.altair_chart(bar(stats, "conversion_%",
                   "Conversion (% of customers with a lead)"), width="stretch")
    b.altair_chart(bar(stats, "median_days_to_decision",
                   "Median days to decide", fmt=",.0f", color="#2a9d8f"), width="stretch")
    c, d = st.columns(2)
    if "late_or_overdue_payments_%" in stats.columns:
        c.altair_chart(bar(stats, "late_or_overdue_payments_%",
                       "Late or overdue payments (%)", color="#e76f51"), width="stretch")
    if "share_of_sale_value_%" in stats.columns:
        d.altair_chart(bar(stats, "share_of_sale_value_%",
                       "Share of total sale value (%)", color="#6a4c93"), width="stretch")
    st.caption(
        "Differences between segments are descriptive. They do not show that a segment causes conversion.")

with tab_test:
    design = load_text("campaign_test_design.md")
    if design:
        st.markdown(design)
    else:
        st.info("The campaign test design is not in app/data/ yet. Run notebook 08, then python app/prepare_app_data.py.")

with tab_mon:
    base = load_csv("segment_baseline_shares.csv", index_col=0)
    if base is not None:
        base = base.iloc[:, 0].rename("baseline_share").reset_index()
        base.columns = ["segment", "baseline_share"]
        base["baseline_share"] *= 100
        st.altair_chart(bar(base, "baseline_share",
                        "Segment sizes when the model was built (% of customers)"), width="stretch")
    drift = load_csv("drift_latest.csv")
    if drift is not None:
        st.subheader("Latest monthly check")
        st.dataframe(drift, width="stretch", hide_index=True)
        st.caption(
            "An alert means a segment's share moved by more than 20% and more than the sampling noise.")
    else:
        st.info("No monthly drift result yet. After the first refresh, save the drift table as outputs/drift_latest.csv and re-run prepare_app_data.py.")
    runbook = load_text("monthly_refresh_runbook.md")
    if runbook:
        with st.expander("Monthly refresh runbook"):
            st.markdown(runbook)

with tab_about:
    card = load_text("MODEL_CARD.md")
    if card:
        st.markdown(card)
    comp = load_csv("candidate_comparison.csv", index_col=0)
    if comp is not None:
        st.subheader("Candidates compared")
        st.dataframe(comp, width="stretch")
    st.caption("Veltrix is a fictional estate agency and the data is synthetic.")
