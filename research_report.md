# Research Report
## Impact of 6G Network Performance on Manufacturing Efficiency in Smart Factories

### Abstract
This study evaluates whether network latency and packet loss are associated with manufacturing efficiency, production speed, error rate and quality-control defect rate in a smart-factory dataset. The analysis combines exploratory data analysis, group comparisons, correlation, regression and categorical association tests. The study deliberately distinguishes statistical association from causal impact.

### 1. Background
Industry 4.0 and emerging Industry 5.0 factories depend on reliable, low-latency machine communication and real-time data exchange. A network issue can reduce operational performance even when mechanical indicators do not immediately show a fault.

### 2. Problem Statement
The objective is to determine whether efficiency variation is associated with latency or packet loss, identify network-performance ranges associated with poorer outcomes, and determine whether operation modes respond differently to network conditions.

### 3. Dataset
The project uses `Thales_Group_Manufacturing.csv`. Variables include machine/operation information, mechanical-process indicators, network latency, packet loss, production speed, error rate, defect rate, predictive-maintenance score and efficiency status.

### 4. Methodology
#### 4.1 Data quality
- Check dimensions, data types and missing values.
- Parse Date + Timestamp into a DateTime field.
- Inspect distributions and outliers.

#### 4.2 Network profiling
- Profile latency and packet-loss distributions.
- Divide latency and packet loss into Low/Medium/High data-driven bands using tertiles.
- Define a combined network-quality label: High, Medium or Low.

#### 4.3 Network vs efficiency
- Compare Efficiency_Status proportions across network-quality groups.
- Use chi-square and Cramér's V to quantify categorical association.
- Plot latency against production speed.

#### 4.4 Latency diagnostics
- Estimate production-speed change per 1 ms of latency using linear regression.
- Report R² and p-value.
- Examine production speed across latency bands to identify dataset-specific sensitivity zones.

#### 4.5 Packet-loss diagnostics
- Test packet loss against error rate and defect rate.
- Compare production speed in low-loss and high-loss groups.
- Calculate Packet Loss Impact Ratio.

#### 4.6 Operation-mode interaction
- Compare Active, Idle and Maintenance modes.
- Repeat network/outcome summaries by operation mode where appropriate.

### 5. KPI Definitions
**Network Stability Index** = 100 × (1 − average normalized network instability), where instability is the mean of normalized latency and normalized packet loss.

**Latency Sensitivity Score** = regression slope of production speed on latency, in units/hour per ms.

**Packet Loss Impact Ratio** = (mean production speed at low packet loss − mean production speed at high packet loss) / mean production speed at low packet loss.

**Network–Efficiency Association** = Pearson/Spearman relationships for continuous outcomes plus chi-square/Cramér's V for Efficiency_Status vs Network_Quality.

### 6. Results
Run the Colab notebook and replace this section with the actual tables and figures generated from the dataset. Do not invent thresholds or causal statements.

### 7. Discussion
A large dataset can produce statistically significant p-values even for very small effects. Therefore, practical effect size, confidence intervals, operational relevance and operation-mode differences should be considered together.

### 8. Recommendations
1. Monitor latency and packet loss as production-health signals alongside machine/process metrics.
2. Use dataset-specific risk zones for alerting, then validate them with controlled factory trials.
3. Prioritize network hardening where a repeatable and practically meaningful relationship with output/error/quality is observed.
4. Avoid diagnosing a production problem as a network problem solely from correlation.

### 9. Limitations
- Observational data cannot by itself establish causality.
- Tertile thresholds are relative to this dataset and should not be treated as universal 6G engineering limits.
- If communication-mode labels are not present, “real-time vs delayed” should be treated as a latency-band proxy rather than a directly observed variable.

### 10. Conclusion
The project evaluates manufacturing performance through a connectivity-first lens. The final conclusion should be based on the observed effect sizes: network variables should be treated as independent operational signals when they show meaningful, repeatable associations after accounting for operation mode and other process variables.
