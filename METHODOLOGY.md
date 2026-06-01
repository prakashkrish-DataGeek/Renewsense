# RenewSense Analytical Methodology Framework

This document outlines the theoretical foundations, score normalisation curves, aggregation calculations, and risk models that drive the composite **Investment Sensitivity Score (ISS)** in RenewSense.

---

## 1. The Seven-Vector ISS Index

To provide an institutional-grade assessment, RenewSense models physical resources, infrastructure capacities, socio-environmental constraints, and regulatory regimes into 7 independent vectors.

```
+-------------------------------------------------------------------------------+
|                       COMPOSITE INVESTMENT SENSITIVITY SCORE                  |
+-------------------------------------------------------------------------------+
       |                   |                   |                   |
+------------+       +-----------+       +-----------+       +-----------+
| SRI (Solar)|       | WRP (Wind)|       | HSI(Water)|       | GIR(Grid) |
+------------+       +-----------+       +-----------+       +-----------+
       |                   |                   |                   |
+------------+       +-----------+       +-----------+       +-----------+
| EVI (Enviro|       | RPE(Policy|       | LSA(Land/ |       |           |
| Volatility)|       |Permitting)|       |Acceptance)|       |           |
+------------+       +-----------+       +-----------+       +-----------+
```

### Vector 1 — Solar Resource Intensity (SRI)
- **Data Source**: ERA5 Global Horizontal Irradiance (GHI) climatology.
- **Metric**: Annual mean GHI ($\text{kWh/m}^2/\text{day}$).
- **Normalisation Curve**: Piecewise linear GHI. Below $1.0 \to 0$, peak yield $5.5 \to 80$, desert max $8.0 \to 100$.

### Vector 2 — Wind Resource Potential (WRP)
- **Data Source**: DTU Global Wind Atlas.
- **Metric**: Wind Power Density ($\text{W/m}^2$) at 100m height.
- **Normalisation Curve**: Sigmoidal/piecewise interpolation. Low resource $<150 \text{ W/m}^2 \to \le 25$, premium yield $>400 \text{ W/m}^2 \to \ge 75$.

### Vector 3 — Hydrological Stress Index (HSI)
- **Data Source**: WRI Aqueduct 4.0 baseline water risk.
- **Metric**: Baseline water stress ratio (0 to 5.0 basin risk scale).
- **Normalisation Curve**: Inverted linear interpolation. Deserts and extreme water scarcity basins score near 0. Humid, water-stable regions score near 100.

### Vector 4 — Grid Infrastructure Readiness (GIR)
- **Data Source**: OpenStreetMap power transmission way structures.
- **Metric**: Euclidean distance to nearest high-voltage (220kV+) power line.
- **Normalisation Curve**: Inverted distance penalties. Under $5\text{km} \to 95$, above $100\text{km} \to 15$, beyond $150\text{km} \to 0$.

### Vector 5 — Environmental Volatility Index (EVI)
- **Data Source**: NOAA extreme events database.
- **Metric**: Frequency of localized Category 3+ extreme events (typhoons, seismic, soil liquefaction).
- **Normalisation Curve**: Discrete event penalties. Stable continental plates score 100. Active geological boundaries score down to 0.

### Vector 6 — Regulatory & Policy Environment (RPE)
- **Data Source**: World Bank Doing Business, IEA IRENA policy indices.
- **Metric**: Policy Strength Tiers (1 to 5).
- **Normalisation Curve**: Permitting duration, binding clean energy targets, PPA currency protections map directly to scores.

### Vector 7 — Land Availability & Social Acceptance (LSA)
- **Data Source**: ESA WorldCover maps, WDPA protected areas databases.
- **Metric**: Net developable land proportion (%) inside circular buffer zone.
- **Normalisation Curve**: Competing agricultural densities, protected forest geofencing, population counts determine developable space.

---

## 2. Mathematical Score Aggregation

Standard index calculations often employ an *arithmetic mean*, which allows strong vectors to mask critical localized flaws. For example, a solar project in a region with outstanding GHI but a transmission line located $200\text{km}$ away would still receive a favorable score.

To enforce capital allocation rigor, RenewSense uses the **Weighted Geometric Mean**:

$$\text{ISS} = \prod_{i=1}^{7} (\text{Score}_i^{W_i})$$

Where:
- $\text{Score}_i$ is the normalized score of vector $i$ $[0.1, 100]$.
- $W_i$ is the normalized scenario weight of vector $i$ ($\sum W_i = 1.0$).

### The Geometric Mean Penalisation Effect
Using a geometric product ensures that **extreme weakness in any single vector heavily penalizes the final composite score**.
- *Example A (Arithmetic)*: Scores $=[95, 95, 95, 95, 95, 95, 10]$ (e.g. outstanding resource, no grid connection). Arithmetic Mean $= 82.8$ (Prime Grade).
- *Example B (Geometric)*: Same scores, Balanced Scenario weights ($1/7$ each). Geometric Mean $= 63.2$ (Moderate Grade). The index successfully penalizes the fatal infrastructure flaw.

---

## 3. Stochastic Uncertainty Analysis

All geospatial inputs carry measurement uncertainties and database lag tolerances. To prevent overconfident capital decisions, RenewSense runs a **Monte Carlo Simulation Engine** (500 stochastic trials) for every site query.
1. Individual vector scores are perturbed using a normal Gaussian distribution:
   $$S_{perturbed} \sim \mathcal{N}(\mu=S_{base}, \sigma=5.0)$$
2. All perturbed scores are clipped to $[0.1, 100]$.
3. Composite ISS is recalculated for each of the 500 trials.
4. The 5th and 95th percentiles of the output distribution form the **90% Confidence Interval** in the dashboard.
5. Marginal impacts (Tornado swings) are derived by shifting one vector score by $\pm 20$ points while keeping others constant, isolating the sensitivity coefficient.
