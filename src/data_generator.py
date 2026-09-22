"""
EV Physics Data Generator Module
Simulates driving trip segments for a 2013 Nissan Leaf (24 kWh battery pack)
based on the University of Michigan Vehicle Energy Dataset (VED) specification.
"""

import numpy as np
import pandas as pd


def generate_ev_dataset(n_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic EV telemetry data based on longitudinal vehicle dynamics,
    ambient temperature degradation, and cabin HVAC draw.

    Parameters
    ----------
    n_samples : int
        Number of trip segments to simulate (default: 5000).
    random_seed : int
        Seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame containing vehicle telemetry features and remaining range.
    """
    np.random.seed(random_seed)

    # 1. Ambient Temperature (deg C) across seasonal operating envelope
    ambient_temp = np.random.uniform(-10.0, 35.0, n_samples)

    # 2. Vehicle Speed (km/h): bimodal distribution for urban and highway driving
    speed_mode = np.random.choice([0, 1], size=n_samples, p=[0.55, 0.45])
    speed = np.where(
        speed_mode == 0,
        np.random.normal(loc=42.0, scale=12.0, size=n_samples),  # Urban / suburban
        np.random.normal(loc=95.0, scale=10.0, size=n_samples),  # Highway
    )
    speed = np.clip(speed, 5.0, 120.0)

    # 3. State of Charge (SoC %)
    soc = np.random.uniform(10.0, 100.0, n_samples)

    # 4. Road Incline / Slope (%)
    road_slope = np.random.normal(loc=0.0, scale=2.0, size=n_samples)
    road_slope = np.clip(road_slope, -6.0, 6.0)

    # 5. Cabin HVAC Power Draw (kW)
    # Heating activates heavily below 12 deg C; A/C activates above 24 deg C
    hvac_power = np.zeros(n_samples)
    cold_mask = ambient_temp < 12.0
    hvac_power[cold_mask] = np.clip(
        (12.0 - ambient_temp[cold_mask]) * 0.25
        + np.random.normal(0.5, 0.3, cold_mask.sum()),
        0.5,
        4.5,
    )
    hot_mask = ambient_temp > 24.0
    hvac_power[hot_mask] = np.clip(
        (ambient_temp[hot_mask] - 24.0) * 0.20
        + np.random.normal(0.4, 0.2, hot_mask.sum()),
        0.3,
        2.5,
    )

    # 6. Battery Chemical Efficiency Factor
    temp_efficiency = np.where(
        ambient_temp < 15.0,
        1.0 - 0.015 * (15.0 - ambient_temp),
        np.where(ambient_temp > 30.0, 1.0 - 0.005 * (ambient_temp - 30.0), 1.0),
    )
    temp_efficiency = np.clip(temp_efficiency, 0.60, 1.0)

    # 7. Usable Battery Energy (Nissan Leaf 24 kWh pack, ~21.5 kWh net usable)
    total_usable_kwh = 21.5
    remaining_kwh = (soc / 100.0) * total_usable_kwh * temp_efficiency

    # 8. Dynamic Energy Consumption Rate (Wh/km)
    base_consumption = 140.0
    speed_drag_penalty = ((speed / 50.0) ** 1.8) * 35.0
    slope_penalty = road_slope * 15.0
    hvac_penalty = (hvac_power * 1000.0) / np.maximum(speed, 10.0)

    total_consumption = base_consumption + speed_drag_penalty + slope_penalty + hvac_penalty
    total_consumption = np.clip(total_consumption, 90.0, 350.0)

    # 9. Target: Remaining Driving Range (km)
    theoretical_range = (remaining_kwh * 1000.0) / total_consumption
    sensor_noise = np.random.normal(loc=0.0, scale=0.03 * theoretical_range)
    remaining_range = np.clip(theoretical_range + sensor_noise, 0.0, 200.0)

    df = pd.DataFrame(
        {
            "speed_kmh": np.round(speed, 1),
            "ambient_temp_c": np.round(ambient_temp, 1),
            "soc_percent": np.round(soc, 1),
            "road_slope_pct": np.round(road_slope, 2),
            "hvac_power_kw": np.round(hvac_power, 2),
            "consumption_wh_per_km": np.round(total_consumption, 1),
            "remaining_range_km": np.round(remaining_range, 1),
        }
    )

    return df
