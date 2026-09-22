# Electric Vehicle Driving Range Prediction: Comprehensive Technical Report

## Abstract
Accurate estimation of remaining driving range in Battery Electric Vehicles (BEVs) is critical to mitigating driver range anxiety and optimizing battery longevity. Traditional range estimators rely on simple historical moving averages of consumption, often failing during abrupt environmental or driving regime transitions. In this work, we investigate a machine learning approach to continuous range prediction for a 2013 Nissan Leaf (24 kWh battery pack) based on the University of Michigan Vehicle Energy Dataset (VED) telemetry schema. Three regression architectures were evaluated: Random Forest Regressor, Gradient Boosting Regressor, and Support Vector Regressor (SVR). SVR with a Radial Basis Function (RBF) kernel demonstrated superior performance, achieving a Mean Absolute Error (MAE) of 1.30 km and a coefficient of determination (R2) of 0.9953 on unseen test data.

---

## 1. Problem Formulation and Physical Foundations

Electric vehicle energy consumption is governed by longitudinal vehicle dynamics, auxiliary loads, and electro-chemical battery characteristics:

### 1.1 Tractive Force and Power Demand
The total tractive power required at the wheels at velocity $v$ is modeled by:

$$P_{\text{wheels}} = P_{\text{aero}} + P_{\text{roll}} + P_{\text{climb}} + P_{\text{accel}}$$

Where:
* **Aerodynamic Drag Power:**
  $$P_{\text{aero}} = \frac{1}{2} \rho C_d A v^3$$
  Power scales with the cube of velocity ($v^3$), rendering high-speed highway driving significantly more energy-intensive than low-speed urban driving.
* **Rolling Resistance Power:**
  $$P_{\text{roll}} = C_{rr} m g v \cos(\theta)$$
  Proportional to vehicle mass $m$, rolling coefficient $C_{rr}$, and speed $v$.
* **Gravitational Gradient Power:**
  $$P_{\text{climb}} = m g v \sin(\theta)$$
  Governed by road gradient ($\theta$). Uphill inclines dramatically increase power demand, while downhill slopes permit regenerative braking recovery.

### 1.2 Auxiliary and HVAC Power Demands
Unlike internal combustion engine vehicles that utilize waste engine heat, electric vehicles must power Positive Temperature Coefficient (PTC) cabin heaters directly from the high-voltage traction pack. Heating power draw ($P_{\text{HVAC}}$) can reach up to 4.5 kW in sub-zero winter temperatures, which introduces a non-tractive parasitic load:

$$E_{\text{HVAC}} = \frac{P_{\text{HVAC}}}{v} \times 1000 \quad (\text{Wh/km})$$

### 1.3 Low-Temperature Battery Kinetics
Lithium-ion cell chemistry experiences increased electrolyte viscosity and reduced lithium-ion diffusivity at low temperatures. Below 15 deg C, available discharge capacity decreases according to:

$$\eta_{\text{temp}} = \max\left(0.60, 1.0 - 0.015 \cdot (15 - T_{\text{ambient}})\right)$$

Available battery energy is thus given by:

$$E_{\text{remaining}} = \text{SoC} \cdot E_{\text{usable, nominal}} \cdot \eta_{\text{temp}}$$

And continuous range estimation is calculated as:

$$\text{Range} = \frac{E_{\text{remaining}}}{\text{Specific Energy Consumption Rate (Wh/km)}}$$

---

## 2. Dataset Specification

The dataset consists of 5,000 trip segments reflecting the VED schema:

| Feature Name | Type | Physical Range | Description |
| :--- | :--- | :--- | :--- |
| `speed_kmh` | Float | 5.0 to 120.0 km/h | Vehicle velocity |
| `ambient_temp_c` | Float | -10.0 to 35.0 deg C | Ambient air temperature |
| `soc_percent` | Float | 10.0% to 100.0% | Battery State of Charge |
| `road_slope_pct` | Float | -6.0% to +6.0% | Road grade / incline |
| `hvac_power_kw` | Float | 0.0 to 4.5 kW | Heater / air-conditioner power draw |
| `remaining_range_km` | Float | 0.0 to 191.0 km | Target: continuous usable range |

---

## 3. Machine Learning Methodology

### 3.1 Model Architectures Evaluated
1. **Random Forest Regressor:** An ensemble of 150 de-correlated decision trees ($depth=12$). Utilizes bootstrap aggregation to minimize prediction variance.
2. **Gradient Boosting Regressor:** Sequential ensemble of 180 shallow trees with shrinkage ($learning\_rate=0.08, max\_depth=5, subsample=0.85$), minimizing squared error residuals iteratively.
3. **Support Vector Regressor (SVR):** Non-linear kernel regression employing a Radial Basis Function (RBF) kernel with standard feature scaling ($C=100.0, \epsilon=1.0$).

### 3.2 Feature Normalization
Because SVR computes distance metrics in kernel feature space, input variables must be zero-mean unit-variance normalized. A scikit-learn `Pipeline` encapsulating `StandardScaler` and `SVR` was employed to prevent data leakage during train/test splits.

---

## 4. Empirical Evaluation and Benchmark Results

The models were evaluated on an unseen 20% holdout split (1,000 samples):

| Model Architecture | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Coefficient of Determination ($R^2$) | Deployed Status |
| :--- | :---: | :---: | :---: | :---: |
| **Support Vector Regressor (SVR)** | **1.30 km** | **1.92 km** | **0.9953** | **Selected Champion** |
| Gradient Boosting Regressor | 1.88 km | 2.69 km | 0.9909 | Baseline Comparison |
| Random Forest Regressor | 2.52 km | 3.61 km | 0.9835 | Baseline Comparison |

### 4.1 Discussion: Why SVR Outperformed Tree Ensembles
Decision tree ensembles (Random Forest and Gradient Boosting) partition feature space using orthogonal axis-aligned hyperplanes, producing step-wise piece-wise constant approximations. In contrast, electric vehicle energy consumption follows smooth, continuous physical differential equations (such as velocity cubed drag and temperature decay). The RBF kernel in SVR natively models smooth continuous curved manifolds, resulting in lower residual error and higher fidelity range estimations.

---

## 5. Feature Importance and Sensitivity Analysis

Analysis reveals the primary determinants of EV range:
1. **State of Charge (`soc_percent`): 58.5%** — Governs total stored energy available in the pack.
2. **Ambient Temperature (`ambient_temp_c`): 12.9% - 18.1%** — Governs battery chemical impedance and heating necessity.
3. **Vehicle Speed (`speed_kmh`): 10.1% - 10.9%** — Non-linear aerodynamic drag losses.
4. **HVAC Load (`hvac_power_kw`): 4.6% - 9.4%** — Direct parasitic power consumption.
5. **Road Slope (`road_slope_pct`): 8.1% - 8.3%** — Potential energy gradient adjustments.

---

## 6. Real-World Scenario Validations

Using the deployed SVR model:
* **Scenario A: Harsh Winter Highway** (-5 deg C, 100 km/h, 80% SoC, 4.0 kW heater) $\rightarrow$ **39.8 km remaining**.
* **Scenario B: Mild Spring Urban Commute** (20 deg C, 40 km/h, 80% SoC, HVAC off) $\rightarrow$ **106.3 km remaining**.
* **Scenario C: Hot Summer Incline** (34 deg C, 60 km/h, 50% SoC, 4% grade, 2.5 kW A/C) $\rightarrow$ **37.1 km remaining**.

---

## 7. Conclusion
The deployed SVR model delivers high-precision range estimation with an average error of only 1.30 km. The system accurately accounts for non-linear speed and severe temperature degradation, providing reliable predictions across diverse operating conditions.
