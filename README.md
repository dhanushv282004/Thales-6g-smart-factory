# Impact of 6G Network Performance on Manufacturing Efficiency in Smart Factories

## Project objective
This project studies whether network performance variables—especially **network latency** and **packet loss**—are associated with manufacturing efficiency, production speed, errors and quality outcomes in a smart-factory dataset.

> **Important research note:** association does not prove that 6G network conditions caused an efficiency change. The analysis therefore reports correlations, group differences and effect sizes, and recommends operational validation before using any value as an engineering threshold.

## Dataset
`data/Thales_Group_Manufacturing.csv` contains 100,000 observations and these fields:

- Date, Timestamp, Machine_ID
- Operation_Mode
- Temperature_C, Vibration_Hz, Power_Consumption_kW
- Network_Latency_ms, Packet_Loss_%
- Quality_Control_Defect_Rate_%
- Production_Speed_units_per_hr
- Predictive_Maintenance_Score
- Error_Rate_%
- Efficiency_Status

## Repository structure
```text
thales-6g-smart-factory/
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── Thales_Group_Manufacturing.csv
└── notebooks/
    └── 6G_Manufacturing_Analysis.ipynb
```

## Google Colab
After pushing this repository to GitHub, open the notebook in Colab with:

```text
https://colab.research.google.com/github/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME/blob/main/notebooks/6G_Manufacturing_Analysis.ipynb
```

Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY_NAME` with your values.

The notebook installs the required libraries, loads the GitHub CSV, performs EDA, creates network-quality bands, calculates KPIs, runs correlation and chi-square diagnostics, and produces presentation-ready charts.

## Run Streamlit locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit deployment
Deploy `app.py` from this GitHub repository using Streamlit Community Cloud. The main file is `app.py`; dependencies are in `requirements.txt`.

## Analytical methodology
1. **Network Performance Profiling** – latency and packet-loss distributions; stable/unstable observations; low/medium/high network-quality bands.
2. **Network vs Efficiency** – compare Efficiency_Status across network-quality groups and inspect latency vs production speed.
3. **Latency Impact Diagnostics** – regression slope, correlation and latency benchmarks.
4. **Packet Loss Impact Diagnostics** – packet-loss vs error/defect relationships and low-vs-high loss production comparison.
5. **Operation Mode Interaction** – compare Active, Idle and Maintenance conditions.
6. **KPI layer** – Network Stability Index, Latency Sensitivity Score, Packet Loss Impact Ratio and Network–Efficiency association.

## KPI definitions
- **Network Stability Index:** 0–100 score created from normalized latency and packet loss; higher is more stable.
- **Latency Sensitivity Score:** regression slope of production speed against latency, expressed as change in units/hour per 1 ms change in latency.
- **Packet Loss Impact Ratio:** `(mean speed at low packet loss - mean speed at high packet loss) / mean speed at low packet loss`.
- **Network–Efficiency Correlation:** Pearson/Spearman association plus a chi-square/Cramér's V test for categorical efficiency vs network quality.

## Submission links
Your submission form asks for four HTTPS links:

1. **GitHub Repository Link** → your GitHub repository.
2. **Research Paper Link** → Google Drive/Docs, journal/preprint page, or another public HTTPS document link.
3. **Deployed Project Link** → your Streamlit application URL.
4. **Project Feedback Video Link** → an unlisted/public YouTube or other HTTPS video URL.

## Suggested research conclusion
The dataset should be used to determine whether network degradation is actually associated with manufacturing outcomes rather than assuming that it is. If effect sizes are small, the defensible conclusion is that network performance is not a strong independent driver in this dataset, and mechanical/process variables may explain more of the observed efficiency variation. If strong relationships appear after controlling for operation mode and machine effects, those relationships can support targeted network-risk benchmarks.
