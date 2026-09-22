"""
Inference Module
Loads the serialized SVR pipeline model and provides prediction utilities.
"""

import os
import sys
import joblib
import pandas as pd


class EVRangePredictor:
    """
    Inference interface for predicting EV driving range using the trained SVR model.
    """

    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "svr_pipeline.joblib")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at {model_path}. Run 'python src/train.py' first."
            )

        self.model = joblib.load(model_path)
        self.feature_names = [
            "speed_kmh",
            "ambient_temp_c",
            "soc_percent",
            "road_slope_pct",
            "hvac_power_kw",
        ]

    def predict(
        self,
        speed_kmh: float,
        ambient_temp_c: float,
        soc_percent: float,
        road_slope_pct: float = 0.0,
        hvac_power_kw: float = 0.0,
    ) -> float:
        """
        Predicts remaining driving range (km) for given input conditions.
        """
        payload = pd.DataFrame(
            [
                [
                    float(speed_kmh),
                    float(ambient_temp_c),
                    float(soc_percent),
                    float(road_slope_pct),
                    float(hvac_power_kw),
                ]
            ],
            columns=self.feature_names,
        )
        prediction = self.model.predict(payload)[0]
        return max(0.0, float(prediction))


if __name__ == "__main__":
    predictor = EVRangePredictor()
    print("EV Driving Range Predictor (SVR Champion Model)")
    print("-" * 50)

    sample_scenarios = [
        ("Sub-zero Winter Highway (-5 deg C, 100 km/h, 80% SoC, 4.0 kW Heater)", 100.0, -5.0, 80.0, 0.0, 4.0),
        ("Mild Spring Urban Commute (20 deg C, 40 km/h, 80% SoC, HVAC Off)", 40.0, 20.0, 80.0, 0.0, 0.0),
        ("Hot Summer Incline (34 deg C, 60 km/h, 50% SoC, 4% Grade, 2.5 kW A/C)", 60.0, 34.0, 50.0, 4.0, 2.5),
    ]

    for label, spd, tmp, soc, slp, hvac in sample_scenarios:
        est_range = predictor.predict(spd, tmp, soc, slp, hvac)
        print(f"{label}")
        print(f"  -> Predicted Remaining Range: {est_range:.2f} km\n")
