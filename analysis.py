"""Core analytics for the 6G smart-factory manufacturing project."""
import numpy as np
import pandas as pd
from scipy import stats

REQUIRED_COLUMNS = [
    "Date", "Timestamp", "Machine_ID", "Operation_Mode", "Temperature_C",
    "Vibration_Hz", "Power_Consumption_kW", "Network_Latency_ms",
    "Packet_Loss_%", "Quality_Control_Defect_Rate_%",
    "Production_Speed_units_per_hr", "Predictive_Maintenance_Score",
    "Error_Rate_%", "Efficiency_Status"
]


def load_data(path="data/Thales_Group_Manufacturing.csv"):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df["DateTime"] = pd.to_datetime(
        df["Date"].astype(str) + " " + df["Timestamp"].astype(str),
        dayfirst=True, errors="coerce"
    )
    return df


def add_network_bands(df):
    out = df.copy()
    # Quantile bands are data-driven and therefore portable to similar datasets.
    # Higher latency / packet loss = poorer network conditions.
    out["Latency_Band"] = pd.qcut(
        out["Network_Latency_ms"], q=3, labels=["Low", "Medium", "High"], duplicates="drop"
    )
    out["Packet_Loss_Band"] = pd.qcut(
        out["Packet_Loss_%"], q=3, labels=["Low", "Medium", "High"], duplicates="drop"
    )
    # Network quality: low/medium/high, where High means better network quality.
    out["Network_Quality"] = np.select(
        [
            (out["Latency_Band"] == "Low") & (out["Packet_Loss_Band"] == "Low"),
            (out["Latency_Band"] == "High") | (out["Packet_Loss_Band"] == "High"),
        ],
        ["High", "Low"], default="Medium"
    )
    return out


def add_kpis(df):
    out = df.copy()
    # Min-max normalization: 0 = best network condition, 1 = worst.
    lat = (out["Network_Latency_ms"] - out["Network_Latency_ms"].min()) / (
        out["Network_Latency_ms"].max() - out["Network_Latency_ms"].min()
    )
    loss = (out["Packet_Loss_%"] - out["Packet_Loss_%"].min()) / (
        out["Packet_Loss_%"].max() - out["Packet_Loss_%"].min()
    )
    out["Network_Instability"] = 0.5 * lat + 0.5 * loss
    out["Network_Stability_Index"] = 100 * (1 - out["Network_Instability"])
    return out


def correlation_table(df):
    cols = [
        "Network_Latency_ms", "Packet_Loss_%", "Production_Speed_units_per_hr",
        "Error_Rate_%", "Quality_Control_Defect_Rate_%"
    ]
    rows = []
    for x in ["Network_Latency_ms", "Packet_Loss_%"]:
        for y in [c for c in cols if c != x]:
            a = df[x].dropna()
            b = df.loc[a.index, y].dropna()
            idx = a.index.intersection(b.index)
            pearson_r, pearson_p = stats.pearsonr(df.loc[idx, x], df.loc[idx, y])
            spearman_r, spearman_p = stats.spearmanr(df.loc[idx, x], df.loc[idx, y])
            rows.append({"Network_Variable": x, "Outcome": y,
                         "Pearson_r": pearson_r, "Pearson_p": pearson_p,
                         "Spearman_rho": spearman_r, "Spearman_p": spearman_p})
    return pd.DataFrame(rows)


def latency_sensitivity(df):
    x = df["Network_Latency_ms"]
    y = df["Production_Speed_units_per_hr"]
    slope, intercept, r, p, se = stats.linregress(x, y)
    return {"slope_units_per_hr_per_ms": slope, "intercept": intercept,
            "r": r, "r2": r*r, "p_value": p, "std_error": se}


def packet_loss_impact_ratio(df):
    low = df.loc[df["Packet_Loss_Band"] == "Low", "Production_Speed_units_per_hr"].mean()
    high = df.loc[df["Packet_Loss_Band"] == "High", "Production_Speed_units_per_hr"].mean()
    ratio = np.nan if low == 0 else (low - high) / low
    return {"low_loss_mean_speed": low, "high_loss_mean_speed": high,
            "impact_ratio": ratio}


def chi_square_efficiency_vs_network(df):
    table = pd.crosstab(df["Network_Quality"], df["Efficiency_Status"])
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.values.sum()
    r, k = table.shape
    cramers_v = np.sqrt((chi2 / n) / max(1, min(r - 1, k - 1)))
    return table, {"chi2": chi2, "p_value": p, "dof": dof, "cramers_v": cramers_v}


def efficiency_summary(df):
    return df.groupby("Efficiency_Status")[[
        "Network_Latency_ms", "Packet_Loss_%", "Production_Speed_units_per_hr",
        "Error_Rate_%", "Quality_Control_Defect_Rate_%"
    ]].agg(["mean", "median"]).round(3)
