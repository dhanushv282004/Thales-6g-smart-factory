#import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from analysis import (
    load_data, add_network_bands, add_kpis, correlation_table,
    data_quality_report, mode_adjusted_ols
)

st.set_page_config(page_title="6G Smart Factory Analytics", page_icon="🏭", layout="wide")


@st.cache_data
def get_data():
    raw = load_data()
    return add_kpis(add_network_bands(raw))


df = get_data()
st.title("🏭 Impact of 6G Network Performance on Manufacturing Efficiency")
st.caption(
    "Exploratory analysis of latency, packet loss, production, quality and errors. "
    "Associations in this observational dataset do not establish causation."
)

with st.sidebar:
    st.header("Filters")
    quality = st.multiselect("Network quality", sorted(df["Network_Quality"].dropna().unique()),
                             default=sorted(df["Network_Quality"].dropna().unique()))
    efficiency = st.multiselect("Efficiency status", sorted(df["Efficiency_Status"].dropna().unique()),
                                default=sorted(df["Efficiency_Status"].dropna().unique()))
    modes = st.multiselect("Operation mode", sorted(df["Operation_Mode"].dropna().unique()),
                           default=sorted(df["Operation_Mode"].dropna().unique()))
    min_date, max_date = df["DateTime"].min().date(), df["DateTime"].max().date()
    dates = st.date_input("Time window", (min_date, max_date), min_value=min_date, max_value=max_date)

f = df[
    df["Network_Quality"].isin(quality)
    & df["Efficiency_Status"].isin(efficiency)
    & df["Operation_Mode"].isin(modes)
].copy()
if isinstance(dates, (tuple, list)) and len(dates) == 2:
    f = f[(f["DateTime"].dt.date >= dates[0]) & (f["DateTime"].dt.date <= dates[1])]

if f.empty:
    st.warning("No records match these filters. Broaden your selection.")
    st.stop()

st.subheader("Headline KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Records in view", f"{len(f):,}")
c2.metric("Mean latency", f"{f['Network_Latency_ms'].mean():.2f} ms")
c3.metric("Mean packet loss", f"{f['Packet_Loss_%'].mean():.2f}%")
c4.metric("Mean relative stability", f"{f['Network_Stability_Index'].mean():.1f}/100")
st.caption(
    "Stability is a dataset-relative min–max score: latency and packet loss are each "
    "scaled across the full loaded dataset, equally weighted, then inverted to 0–100. "
    "It is not an industry SLA, and does not independently certify network reliability."
)

with st.expander("Data-quality checks", expanded=False):
    st.dataframe(data_quality_report(df), use_container_width=True)
    st.caption("Checks flag issues for review; they do not automatically repair or remove records.")

st.subheader("1. Network trends")
# Aggregate by day to reduce timestamp-level noise; show daily mean and 7-day rolling mean.
trend = f.set_index("DateTime")[["Network_Latency_ms", "Packet_Loss_%"]].resample("D").mean()
trend = trend.dropna(how="all")
if not trend.empty:
    trend["Latency_7d_rolling"] = trend["Network_Latency_ms"].rolling(7, min_periods=1).mean()
    trend["Loss_7d_rolling"] = trend["Packet_Loss_%"].rolling(7, min_periods=1).mean()
    t1, t2 = st.columns(2)
    with t1:
        fig = px.line(trend.reset_index(), x="DateTime",
                      y=["Network_Latency_ms", "Latency_7d_rolling"],
                      title="Daily latency (daily mean and 7-day rolling mean)")
        fig.update_layout(legend_title_text="Series")
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        fig = px.line(trend.reset_index(), x="DateTime",
                      y=["Packet_Loss_%", "Loss_7d_rolling"],
                      title="Daily packet loss (daily mean and 7-day rolling mean)")
        fig.update_layout(legend_title_text="Series")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No valid timestamps in the selected records.")

st.subheader("2. Network vs production")
# Smaller sample + transparency about sample size; WebGL rendering and opacity reduce overplotting.
sample_n = min(4000, len(f))
sample = f.sample(sample_n, random_state=42) if len(f) > sample_n else f
st.caption(f"Scatter plots display {len(sample):,} sampled rows out of {len(f):,} filtered records.")
p1, p2 = st.columns(2)
with p1:
    fig = px.scatter(sample, x="Network_Latency_ms", y="Production_Speed_units_per_hr",
                     color="Efficiency_Status", hover_data=["Packet_Loss_%", "Operation_Mode"],
                     title="Latency vs production speed")
    fig.update_traces(marker=dict(opacity=0.35, size=5))
    fig.update_layout(dragmode="zoom")
    st.plotly_chart(fig, use_container_width=True)
with p2:
    fig = px.scatter(sample, x="Packet_Loss_%", y="Production_Speed_units_per_hr",
                     color="Operation_Mode", hover_data=["Network_Latency_ms", "Efficiency_Status"],
                     title="Packet loss vs production speed")
    fig.update_traces(marker=dict(opacity=0.35, size=5))
    fig.update_layout(dragmode="zoom")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("3. Quality and error patterns")
q1, q2 = st.columns(2)
with q1:
    fig = px.scatter(sample, x="Packet_Loss_%", y="Error_Rate_%",
                     color="Operation_Mode", title="Packet loss vs error rate")
    fig.update_traces(marker=dict(opacity=0.30, size=5))
    st.plotly_chart(fig, use_container_width=True)
with q2:
    fig = px.scatter(sample, x="Packet_Loss_%", y="Quality_Control_Defect_Rate_%",
                     color="Operation_Mode", title="Packet loss vs defect rate")
    fig.update_traces(marker=dict(opacity=0.30, size=5))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("4. Compare operation modes")
mode_summary = f.groupby("Operation_Mode").agg(
    Records=("Operation_Mode", "size"),
    Mean_Latency_ms=("Network_Latency_ms", "mean"),
    Mean_Packet_Loss_pct=("Packet_Loss_%", "mean"),
    Mean_Production_Speed=("Production_Speed_units_per_hr", "mean"),
    Mean_Error_Rate_pct=("Error_Rate_%", "mean"),
    Mean_Defect_Rate_pct=("Quality_Control_Defect_Rate_%", "mean"),
    Mean_Relative_Stability=("Network_Stability_Index", "mean")
).reset_index()
st.dataframe(mode_summary.round(3), use_container_width=True)

st.subheader("5. Statistical diagnostics")
corr = correlation_table(f)
st.dataframe(corr.round(4), use_container_width=True)
st.info(
    "Interpret correlation magnitude and units alongside p-values. With many records, "
    "small associations can be statistically significant yet operationally minor. "
    "These are observational associations, not causal effects."
)

st.markdown("#### Exploratory multivariable model: production speed")
st.write("OLS includes latency, packet loss and operation-mode indicators. Coefficients are adjusted associations, not causal estimates.")
coefficients, model_info = mode_adjusted_ols(f)
if not coefficients.empty:
    st.metric("Model R²", f"{model_info['r_squared']:.3f}" if pd.notna(model_info["r_squared"]) else "N/A")
    st.caption(f"Complete-case rows: {model_info['n']:,}. {model_info['message']}")
    st.dataframe(coefficients.round(4), use_container_width=True)
else:
    st.warning(model_info["message"])

st.subheader("6. Dataset-relative alerts and optimization prompts")
lat_cut = f["Network_Latency_ms"].quantile(0.95)
loss_cut = f["Packet_Loss_%"].quantile(0.95)
alerts = f[(f["Network_Latency_ms"] >= lat_cut) | (f["Packet_Loss_%"] >= loss_cut)].copy()
a1, a2, a3 = st.columns(3)
a1.metric("95th percentile latency", f"{lat_cut:.2f} ms")
a2.metric("95th percentile packet loss", f"{loss_cut:.2f}%")
a3.metric("Rows flagged (either metric)", f"{len(alerts):,}")
st.caption("These are relative flags within the currently filtered slice—not validated alarm limits.")
st.write("Suggested investigation steps (validate with plant/network engineers before acting):")
st.markdown(
    "- Compare flagged records by machine and operation mode; check whether anomalies cluster.\n"
    "- Inspect equipment/network logs around flagged timestamps and verify sensor quality.\n"
    "- Test network changes in a controlled pilot; measure production, error and defect outcomes.\n"
    "- Establish operational alarm thresholds using requirements, baseline data and engineering review."
)
if not alerts.empty:
    st.download_button("Download flagged records", alerts.to_csv(index=False).encode("utf-8"),
                       "6g_relative_alert_records.csv", "text/csv")

st.subheader("7. Download")
st.download_button("Download filtered records", f.to_csv(index=False).encode("utf-8"),
                    "filtered_6g_manufacturing.csv", "text/csv")
summary_csv = mode_summary.to_csv(index=False).encode("utf-8")
st.download_button("Download operation-mode summary", summary_csv,
                   "6g_operation_mode_summary.csv", "text/csv")
