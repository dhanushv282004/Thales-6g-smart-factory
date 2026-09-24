# Research Report
## Impact of 6G Network Performance on Manufacturing Efficiency in Smart Factories

### Abstract
This study evaluates whether network latency and packet loss are associated with manufacturing efficiency, production speed, error rate and quality-control defect rate in a smart-factory dataset. The analysis combines exploratory data analysis, network-quality grouping, correlation, linear regression, packet-loss impact analysis, operation-mode comparison and categorical association testing. The study deliberately distinguishes statistical association from causal impact.

The dataset contains 100,000 manufacturing observations and 14 variables. The analysis found very weak observed relationships between the network variables and the manufacturing outcomes examined. Network quality and Efficiency_Status showed a very small categorical association (Cramér's V = 0.0030; chi-square p = 0.7703). The estimated latency sensitivity was -0.0097 production units per hour per additional millisecond of latency, with R² approximately 0.000001 and p = 0.7399. The Packet Loss Impact Ratio was 0.007703, or approximately 0.77%. These results indicate that network performance was not a strong independent explanatory factor for the observed manufacturing outcomes in this dataset. Because the data are observational, these findings do not establish causality.

### 1. Background
Industry 4.0 and emerging Industry 5.0 factories depend on reliable, low-latency machine communication and real-time data exchange. A network issue can reduce operational performance even when mechanical indicators do not immediately show a fault.

### 2. Problem Statement
The objective is to determine whether efficiency variation is associated with latency or packet loss, identify network-performance ranges associated with poorer outcomes, and determine whether operation modes respond differently to network conditions.

### 3. Dataset
The project uses `Thales_Group_Manufacturing.csv`. The dataset contains 100,000 observations and 14 columns covering machine and operation information, mechanical-process indicators, network latency, packet loss, production speed, error rate, quality-control defect rate, predictive-maintenance score and efficiency status.

The dataset contained no missing values in the inspected columns. The analysis also combined `Date` and `Timestamp` into a `DateTime` field for time-based analysis.

### 4. Methodology

#### 4.1 Data quality
- Checked dimensions, data types and missing values.
- Parsed Date + Timestamp into a DateTime field.
- Inspected descriptive statistics and distributions.

#### 4.2 Network profiling
- Profiled latency and packet-loss distributions.
- Divided latency and packet loss into Low/Medium/High data-driven bands using tertiles.
- Defined a combined network-quality label:
  - High: low latency and low packet loss.
  - Low: high latency or high packet loss.
  - Medium: all other combinations.

#### 4.3 Network vs efficiency
- Compared Efficiency_Status proportions across network-quality groups.
- Used chi-square and Cramér's V to quantify categorical association.
- Examined latency against production speed.

#### 4.4 Latency diagnostics
- Estimated production-speed change per 1 ms of latency using linear regression.
- Reported slope, R² and p-value.
- Examined production speed across latency observations.

#### 4.5 Packet-loss diagnostics
- Examined packet loss against error rate and defect rate.
- Compared production speed in low-loss and high-loss groups.
- Calculated the Packet Loss Impact Ratio.

#### 4.6 Operation-mode interaction
- Compared Active, Idle and Maintenance modes.
- Summarized network and manufacturing outcomes within each operation mode.

### 5. KPI Definitions

**Network Stability Index** = 100 × (1 − average normalized network instability), where instability is the mean of normalized latency and normalized packet loss.

**Latency Sensitivity Score** = regression slope of production speed on latency, in units/hour per ms.

**Packet Loss Impact Ratio** = (mean production speed at low packet loss − mean production speed at high packet loss) / mean production speed at low packet loss.

**Network–Efficiency Association** = Pearson/Spearman relationships for continuous outcomes plus chi-square/Cramér's V for Efficiency_Status vs Network_Quality.

### 6. Results

#### 6.1 Data quality and network profile

The analysis used 100,000 observations across 14 variables. No missing values were detected in the inspected dataset.

The network-quality grouping produced the following distribution:

| Network Quality | Observations | Share |
|---|---:|---:|
| High | 11,163 | 11.16% |
| Medium | 33,239 | 33.24% |
| Low | 55,598 | 55.60% |
| **Total** | **100,000** | **100.00%** |

The observed network variables ranged from approximately 1 to 50 ms for latency and 0% to 5% for packet loss. The overall mean latency was approximately 25.56 ms and the overall mean packet loss was approximately 2.49%.

These network-quality categories are dataset-relative tertile-based classifications and should not be interpreted as universal 6G engineering limits.

#### 6.2 Network quality and efficiency status

The proportions of Efficiency_Status within each network-quality group were very similar:

| Network Quality | High Efficiency | Low Efficiency | Medium Efficiency |
|---|---:|---:|---:|
| High | 2.9% | 77.6% | 19.6% |
| Low | 3.0% | 77.9% | 19.2% |
| Medium | 3.0% | 77.9% | 19.1% |

The chi-square test gave χ² = 1.8119 with p = 0.7703. Cramér's V was 0.0030. The very small Cramér's V indicates that the observed categorical association between network quality and efficiency status was negligible in this dataset.

#### 6.3 Latency and production speed

The estimated Latency Sensitivity Score was:

**-0.0097 units/hour per 1 ms increase in latency.**

The regression produced R² approximately equal to 0.000001 and p = 0.7399. The corresponding Pearson correlation between latency and production speed was approximately -0.0010.

The near-zero R² indicates that latency explained virtually none of the observed variation in production speed in this analysis. The p-value also does not provide evidence of a statistically detectable linear relationship in this dataset.

#### 6.4 Packet loss and manufacturing outcomes

The Pearson correlations were close to zero:

| Network Variable | Outcome | Pearson r |
|---|---|---:|
| Packet loss | Production speed | -0.0071 |
| Packet loss | Error rate | -0.0024 |
| Packet loss | Defect rate | -0.0049 |
| Latency | Production speed | -0.0010 |
| Latency | Error rate | 0.0001 |
| Latency | Defect rate | -0.0044 |

The Packet Loss Impact Ratio was **0.007703**, equivalent to approximately **0.77%**.

This indicates only a small difference in mean production speed between the low-loss and high-loss groups under the project's defined calculation. The observed correlations between packet loss and error/defect outcomes were also close to zero.

#### 6.5 Operation-mode analysis

The mean values by operation mode were:

| Operation Mode | Latency (ms) | Packet Loss (%) | Production Speed (units/hr) | Error Rate (%) | Defect Rate (%) |
|---|---:|---:|---:|---:|---:|
| Active | 25.539 | 2.493 | 276.199 | 7.494 | 5.009 |
| Idle | 25.640 | 2.501 | 274.126 | 7.523 | 5.010 |
| Maintenance | 25.502 | 2.480 | 277.544 | 7.537 | 5.001 |

The averages are close across the three operation modes. In particular, average latency and packet loss vary only slightly between modes, while the manufacturing and quality measures also remain similar.

#### 6.6 KPI results

| KPI | Result |
|---|---:|
| Network Stability Index | **50.009 / 100** |
| Latency Sensitivity Score | **-0.0097 units/hour/ms** |
| Packet Loss Impact Ratio | **0.007703 (0.77%)** |
| Network–Efficiency Cramér's V | **0.0030** |
| Network quality vs Efficiency p-value | **0.7703** |
| Latency regression R² | **~0.000001** |
| Latency regression p-value | **0.7399** |

The Network Stability Index is a composite descriptive score based on the project's min-max normalization and equal weighting of latency and packet loss. It should therefore be interpreted as a dataset-specific KPI rather than as a standardized 6G network benchmark.

### 7. Discussion

The results provide little evidence of a strong statistical relationship between the measured network variables and the manufacturing outcomes in this dataset. The network-quality/efficiency association was extremely small, with Cramér's V = 0.0030. Similarly, the latency-production-speed regression had an almost zero R² and a p-value of 0.7399.

The packet-loss results were also weak. The Packet Loss Impact Ratio was approximately 0.77%, while the correlations between packet loss and production speed, error rate and defect rate were all close to zero.

These results should not be interpreted as proof that network performance is irrelevant to smart-factory operations. The analysis is observational, and the dataset may contain other variables or relationships that explain manufacturing variation. The results instead indicate that, within this particular dataset and analytical design, latency and packet loss do not appear to be strong independent explanatory variables for the measured manufacturing outcomes.

The similarity of the operation-mode averages also suggests that the observed network and manufacturing measures were relatively stable across Active, Idle and Maintenance conditions. More detailed multivariable or controlled experimental analysis would be required to isolate network effects from machine, process and operational factors.

### 8. Recommendations

1. Continue monitoring latency and packet loss as production-health signals alongside machine and process metrics.
2. Use the dataset-specific tertile bands and quartile benchmarks for exploratory monitoring only, not as universal engineering limits.
3. Validate any proposed latency or packet-loss thresholds through controlled factory experiments or additional operational data.
4. Avoid diagnosing a production problem as a network problem solely from correlation or group comparison.
5. If future data are available, include machine-level effects, time effects and additional process variables in multivariable models to better isolate network-related variation.
6. For deployment, use the Streamlit dashboard as a monitoring and diagnostic interface rather than as a causal decision system.

### 9. Limitations

- The observational dataset cannot by itself establish causality.
- Tertile-based network-quality thresholds are relative to this dataset and should not be treated as universal 6G engineering limits.
- The dataset does not directly contain a communication-mode label distinguishing real-time from delayed communication. Therefore, latency bands should be treated as an operational proxy rather than a directly observed communication mode.
- Very small effects can be statistically difficult to interpret operationally in a large dataset; practical effect size should be considered together with p-values.
- The current analysis does not constitute a controlled experiment and does not fully adjust for all possible machine- or process-level confounding factors.

### 10. Conclusion

This study evaluated the relationship between network performance and manufacturing outcomes using 100,000 smart-factory observations. The analysis examined network quality, latency, packet loss, production speed, efficiency status, error rate, defect rate and operation mode.

Across the tested relationships, the observed effects were very small. Network quality had a negligible association with Efficiency_Status (Cramér's V = 0.0030), latency showed an almost zero relationship with production speed (slope = -0.0097 units/hour/ms; R² ≈ 0.000001; p = 0.7399), and the Packet Loss Impact Ratio was approximately 0.77%.

Therefore, the dataset does not provide evidence of a strong independent association between the measured network-performance variables and the manufacturing outcomes examined. This conclusion is specific to the dataset and methodology used and should not be generalized to all 6G smart-factory environments. Future work should incorporate richer time-series data, machine-level effects, controlled network experiments and multivariable models to determine whether network degradation becomes operationally important under specific production conditions.
