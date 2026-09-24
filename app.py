import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from analysis import load_data, add_network_bands, add_kpis, correlation_table


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="6G Smart Factory Analytics",
    page_icon="🏭",
    layout="wide"
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def get_data():
    return add_kpis(add_network_bands(load_data()))


df = get_data()


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("🏭 Impact of 6G Network Performance on Manufacturing Efficiency")

st.caption(
    "Network-first analytics for latency, packet loss, efficiency, "
    "quality and errors in smart factories."
)


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
with st.sidebar:

    st.header("Filters")

    quality = st.multiselect(
        "Network quality",
        sorted(df["Network_Quality"].unique()),
        default=sorted(df["Network_Quality"].unique())
    )

    efficiency = st.multiselect(
        "Efficiency status",
        sorted(df["Efficiency_Status"].unique()),
        default=sorted(df["Efficiency_Status"].unique())
    )

    modes = st.multiselect(
        "Operation mode",
        sorted(df["Operation_Mode"].unique()),
        default=sorted(df["Operation_Mode"].unique())
    )

    min_date = df["DateTime"].min().date()
    max_date = df["DateTime"].max().date()

    dates = st.date_input(
        "Time window",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
f = df[
    df["Network_Quality"].isin(quality)
    & df["Efficiency_Status"].isin(efficiency)
    & df["Operation_Mode"].isin(modes)
].copy()


if isinstance(dates, tuple) and len(dates) == 2:

    f = f[
        (f["DateTime"].dt.date >= dates[0])
        & (f["DateTime"].dt.date <= dates[1])
    ]


# ---------------------------------------------------------
# NO DATA MESSAGE
# ---------------------------------------------------------
if len(f) == 0:

    st.warning(
        "No records match the selected filters. "
        "Please select a broader filter range."
    )

else:

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Records",
        f"{len(f):,}"
    )

    c2.metric(
        "Avg latency",
        f"{f['Network_Latency_ms'].mean():.2f} ms"
    )

    c3.metric(
        "Avg packet loss",
        f"{f['Packet_Loss_%'].mean():.2f}%"
    )

    c4.metric(
        "Avg stability index",
        f"{f['Network_Stability_Index'].mean():.1f}/100"
    )


    # -----------------------------------------------------
    # 1. NETWORK PERFORMANCE OVERVIEW
    # -----------------------------------------------------
    st.subheader("1. Network Performance Overview")

    col1, col2 = st.columns(2)

    trend = (
        f.groupby("DateTime", as_index=False)
        [["Network_Latency_ms", "Packet_Loss_%"]]
        .mean()
    )

    with col1:

        fig_latency = px.line(
            trend,
            x="DateTime",
            y="Network_Latency_ms",
            title="Latency Trend"
        )

        st.plotly_chart(
            fig_latency,
            use_container_width=True
        )

    with col2:

        fig_loss = px.line(
            trend,
            x="DateTime",
            y="Packet_Loss_%",
            title="Packet-Loss Trend"
        )

        st.plotly_chart(
            fig_loss,
            use_container_width=True
        )


    # -----------------------------------------------------
    # SAMPLE DATA FOR SCATTER PLOTS
    # -----------------------------------------------------
    sample = f.sample(
        min(8000, len(f)),
        random_state=42
    )


    # -----------------------------------------------------
    # 2. NETWORK VS EFFICIENCY
    # -----------------------------------------------------
    st.subheader("2. Network vs Efficiency")

    col1, col2 = st.columns(2)

    with col1:

        g = (
            f.groupby(
                ["Network_Quality", "Efficiency_Status"]
            )
            .size()
            .reset_index(name="Count")
        )

        fig_efficiency = px.bar(
            g,
            x="Network_Quality",
            y="Count",
            color="Efficiency_Status",
            barmode="group",
            title="Efficiency Distribution by Network Quality"
        )

        st.plotly_chart(
            fig_efficiency,
            use_container_width=True
        )

    with col2:

        fig_speed = px.scatter(
            sample,
            x="Network_Latency_ms",
            y="Production_Speed_units_per_hr",
            color="Efficiency_Status",
            hover_data=[
                "Packet_Loss_%",
                "Operation_Mode"
            ],
            title="Latency vs Production Speed"
        )

        st.plotly_chart(
            fig_speed,
            use_container_width=True
        )


    # -----------------------------------------------------
    # 3. QUALITY & ERROR IMPACT
    # -----------------------------------------------------
    st.subheader("3. Quality & Error Impact")

    col1, col2 = st.columns(2)

    with col1:

        fig_error = px.scatter(
            sample,
            x="Packet_Loss_%",
            y="Error_Rate_%",
            color="Operation_Mode",
            title="Packet Loss vs Error Rate"
        )

        st.plotly_chart(
            fig_error,
            use_container_width=True
        )

    with col2:

        fig_defect = px.scatter(
            sample,
            x="Packet_Loss_%",
            y="Quality_Control_Defect_Rate_%",
            color="Operation_Mode",
            title="Packet Loss vs Defect Rate"
        )

        st.plotly_chart(
            fig_defect,
            use_container_width=True
        )


    # -----------------------------------------------------
    # 4. OPERATION MODE INTERACTION
    # -----------------------------------------------------
    st.subheader("4. Operation Mode Interaction")

    mode_summary = (
        f.groupby("Operation_Mode")
        [[
            "Network_Latency_ms",
            "Packet_Loss_%",
            "Production_Speed_units_per_hr",
            "Error_Rate_%",
            "Quality_Control_Defect_Rate_%",
            "Network_Stability_Index"
        ]]
        .mean()
        .reset_index()
    )

    st.dataframe(
        mode_summary.round(3),
        use_container_width=True
    )


    # -----------------------------------------------------
    # 5. KPI & STATISTICAL DIAGNOSTICS
    # -----------------------------------------------------
    st.subheader("5. KPI & Statistical Diagnostics")

    if len(f) >= 2:

        corr = correlation_table(f)

        st.dataframe(
            corr.round(5),
            use_container_width=True
        )

    else:

        st.info(
            "At least 2 records are required to calculate "
            "statistical correlations. Please select a broader filter range."
        )


    st.info(
        "Interpretation rule: statistical association is not proof of causation. "
        "Use p-values together with effect size (r, Spearman rho, or "
        "Cramér's V) and operational context."
    )


    # -----------------------------------------------------
    # 6. OPTIMIZATION INSIGHTS
    # -----------------------------------------------------
    st.subheader("6. Optimization Insights")

    lat_q = f[
        "Network_Latency_ms"
    ].quantile(
        [.25, .50, .75]
    ).to_dict()

    loss_q = f[
        "Packet_Loss_%"
    ].quantile(
        [.25, .50, .75]
    ).to_dict()

    st.write(
        f"**Latency benchmarks (dataset quartiles):** "
        f"Q1={lat_q[0.25]:.2f} ms, "
        f"Median={lat_q[0.50]:.2f} ms, "
        f"Q3={lat_q[0.75]:.2f} ms."
    )

    st.write(
        f"**Packet-loss benchmarks:** "
        f"Q1={loss_q[0.25]:.2f}%, "
        f"Median={loss_q[0.50]:.2f}%, "
        f"Q3={loss_q[0.75]:.2f}%."
    )

    st.write(
        "Treat the upper quartile as a risk-monitoring zone rather than "
        "a universal engineering limit; validate thresholds with production "
        "experiments and domain requirements."
    )


    # -----------------------------------------------------
    # DOWNLOAD FILTERED DATA
    # -----------------------------------------------------
    st.download_button(
        "Download filtered data",
        f.to_csv(index=False).encode("utf-8"),
        "filtered_6g_manufacturing.csv",
        "text/csv"
    )
