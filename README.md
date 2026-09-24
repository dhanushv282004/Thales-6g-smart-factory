# Impact of 6G Network Performance on Manufacturing Efficiency in Smart Factories

## Project Objective

This project studies whether network performance variables—especially **network latency** and **packet loss**—are associated with manufacturing efficiency, production speed, errors, and quality outcomes in a smart-factory dataset.

> **Important Research Note:** Association does not prove that 6G network conditions caused an efficiency change. The analysis therefore reports correlations, group differences, and effect sizes, and recommends operational validation before using any value as an engineering threshold.

## Dataset

The project uses `data/Thales_Group_Manufacturing.csv`, which contains **100,000 observations** and the following fields:

- Date
- Timestamp
- Machine_ID
- Operation_Mode
- Temperature_C
- Vibration_Hz
- Power_Consumption_kW
- Network_Latency_ms
- Packet_Loss_%
- Quality_Control_Defect_Rate_%
- Production_Speed_units_per_hr
- Predictive_Maintenance_Score
- Error_Rate_%
- Efficiency_Status

## Repository Structure

```text
Thales-6g-smart-factory/
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── Thales_Group_Manufacturing.csv
└── notebooks/
    └── 6G_Manufacturing_Analysis.ipynb
