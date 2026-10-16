"""Core analytics for the 6G smart-factory manufacturing project.

Scores and risk bands in this module are dataset-relative diagnostics, not
validated industrial/network service-level thresholds.
"""
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

NUMERIC_COLUMNS = [
    "Temperature_C", "Vibration_Hz", "Power_Consumption_kW",
    "Network_Latency_ms", "Packet_Loss_%",
    "Quality_Control_Defect_Rate_%",
    "Production_Speed_units_per_hr", "Predictive_Maintenance_Score",
    "Error_Rate_%"
]


def load_data(path="data/Thales_Group_Manufacturing.csv"):
    """Load data and validate schema, parse timestamps, and coerce numeric fields."""
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["DateTime"] = pd.to_datetime(
        df["Date"].astype(str) + " " + df["Timestamp"].astype(str),
        dayfirst=True, errors="coerce"
    )
    return df


def data_quality_report(df):
    """Return a compact, transparent data-quality summary."""
    numeric = [c for c in NUMERIC_COLUMNS if c in df.columns]
    return pd.DataFrame({
        "Check": [
            "Rows",
            "Duplicate rows",
            "Invalid/unparsed timestamps",
            "Missing numeric values (cells)",
            "Negative latency records",
            "Negative packet-loss records",
            "Negative production-speed records",
            "Unexpected efficiency labels"
        ],
        "Result": [
            len(df),
            int(df.duplicated().sum()),
            int(df["DateTime"].isna().sum()) if "DateTime" in df else np.nan,
            int(df[numeric].isna().sum().sum()),
            int((df["Network_Latency_ms"] < 0).sum()),
            int((df["Packet_Loss_%"] < 0).sum()),
            int((df["Production_Speed_units_per_hr"] < 0).sum()),
            int(df["Efficiency_Status"].isna().sum())
        ]
    })


def _tertile_band(series):
    """Quantile bands robust to tied/constant values."""
    rank = series.rank(method="average", pct=True)
    return pd.cut(rank, bins=[0, 1/3, 2/3, 1.0000001],
                  labels=["Low", "Medium", "High"], include_lowest=True)


def add_network_bands(df):
    out = df.copy()
    out["Latency_Band"] = _tertile_band(out["Network_Latency_ms"])
    out["Packet_Loss_Band"] = _tertile_band(out["Packet_Loss_%"])
    # High quality means both metrics fall in their lower (better) tertile.
    out["Network_Quality"] = np.select(
        [
            (out["Latency_Band"] == "Low") & (out["Packet_Loss_Band"] == "Low"),
            (out["Latency_Band"] == "High") | (out["Packet_Loss_Band"] == "High"),
        ],
        ["High", "Low"], default="Medium"
    )
    return out


def add_kpis(df):
    """Dataset-relative min-max stability score; not an engineering SLA."""
    out = df.copy()

    def scaled(series):
        lo, hi = series.min(), series.max()
        if pd.isna(lo) or pd.isna(hi):
            return pd.Series(np.nan, index=series.index)
        if hi == lo:
            # All observations are equal: no relative variation to penalize.
            return pd.Series(0.0, index=series.index)
        return (series - lo) / (hi - lo)

    lat = scaled(out["Network_Latency_ms"])
    loss = scaled(out["Packet_Loss_%"])
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
            pair = df[[x, y]].dropna()
            if len(pair) < 3 or pair[x].nunique() < 2 or pair[y].nunique() < 2:
                pearson_r = pearson_p = spearman_rho = spearman_p = np.nan
            else:
                pearson_r, pearson_p = stats.pearsonr(pair[x], pair[y])
                spearman_rho, spearman_p = stats.spearmanr(pair[x], pair[y])
            rows.append({
                "Network_Variable": x, "Outcome": y, "N": len(pair),
                "Pearson_r": pearson_r, "Pearson_p": pearson_p,
                "Spearman_rho": spearman_rho, "Spearman_p": spearman_p,
                "Effect_size_note": "Report magnitude and operational relevance; p-value alone is insufficient."
            })
    return pd.DataFrame(rows)


def mode_adjusted_ols(df, outcome="Production_Speed_units_per_hr"):
    """OLS association model controlling for operation mode.

    Predictors: latency, packet loss, and operation-mode indicator variables.
    This is observational and should not be interpreted as causal.
    """
    cols = [outcome, "Network_Latency_ms", "Packet_Loss_%", "Operation_Mode"]
    data = df[cols].dropna().copy()
    if len(data) < 10 or data["Operation_Mode"].nunique() < 2:
        return pd.DataFrame(), {"n": len(data), "r_squared": np.nan,
                                "message": "Need at least 10 complete rows and 2 operation modes."}

    mode = pd.get_dummies(data["Operation_Mode"].astype(str), prefix="mode",
                          drop_first=True, dtype=float)
    X = pd.concat([
        pd.Series(1.0, index=data.index, name="Intercept"),
        data[["Network_Latency_ms", "Packet_Loss_%"]].astype(float),
        mode
    ], axis=1)
    y = data[outcome].astype(float)
    matrix = X.to_numpy(dtype=float)
    target = y.to_numpy(dtype=float)
    beta, _, _, _ = np.linalg.lstsq(matrix, target, rcond=None)
    fitted = matrix @ beta
    ss_res = float(np.sum((target - fitted) ** 2))
    ss_tot = float(np.sum((target - target.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    coefficients = pd.DataFrame({
        "Term": X.columns,
        "Coefficient": beta,
        "Interpretation": [
            "Baseline at zero-valued numeric predictors/reference mode; not necessarily meaningful."
            if term == "Intercept" else
            "Adjusted association, holding included predictors constant; not causal."
            for term in X.columns
        ]
    })
    return coefficients, {
        "n": len(data), "r_squared": r2,
        "outcome": outcome,
        "predictors": "Latency, packet loss, operation mode indicators",
        "message": "Exploratory OLS association model; omitted factors and observational data limit causal interpretation."
    }


def latency_sensitivity(df):
    pair = df[["Network_Latency_ms", "Production_Speed_units_per_hr"]].dropna()
    if len(pair) < 3 or pair["Network_Latency_ms"].nunique() < 2:
        return {"slope_units_per_hr_per_ms": np.nan, "intercept": np.nan,
                "r": np.nan, "r2": np.nan, "p_value": np.nan, "std_error": np.nan}
    slope, intercept, r, p, se = stats.linregress(
        pair["Network_Latency_ms"], pair["Production_Speed_units_per_hr"])
    return {"slope_units_per_hr_per_ms": slope, "intercept": intercept,
            "r": r, "r2": r*r, "p_value": p, "std_error": se}


def packet_loss_impact_ratio(df):
    low = df.loc[df["Packet_Loss_Band"] == "Low", "Production_Speed_units_per_hr"].mean()
    high = df.loc[df["Packet_Loss_Band"] == "High", "Production_Speed_units_per_hr"].mean()
    ratio = np.nan if pd.isna(low) or low == 0 else (low - high) / low
    return {"low_loss_mean_speed": low, "high_loss_mean_speed": high,
            "impact_ratio": ratio}


def chi_square_efficiency_vs_network(df):
    table = pd.crosstab(df["Network_Quality"], df["Efficiency_Status"])
    if table.empty or min(table.shape) < 2:
        return table, {"chi2": np.nan, "p_value": np.nan, "dof": 0, "cramers_v": np.nan}
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.values.sum()
    r, k = table.shape
    cramers_v = np.sqrt((chi2 / n) / max(1, min(r - 1, k - 1)))
    return table, {"chi2": chi2, "p_value": p, "dof": dof, "cramers_v": cramers_v}


def efficiency_summary(df):
    return df.groupby("Efficiency_Status")[[
        "Network_Latency_ms", "Packet_Loss_%", "Production_Speed_units_per_hr",
        "Error_Rate_%", "Quality_Control_Defect_Rate_%"
    ]].agg(["mean", "median", "count"]).round(3)
