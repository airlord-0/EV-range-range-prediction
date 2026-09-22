"""
Model Training and Benchmarking Module
Trains Random Forest, Gradient Boosting, and Support Vector Regressor (SVR).
Saves the champion model (SVR) to models/svr_pipeline.joblib.
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_generator import generate_ev_dataset


def train_and_evaluate(project_root: str):
    """
    Executes the complete training workflow:
    1. Generates or loads the dataset
    2. Trains and benchmarks Random Forest, Gradient Boosting, and SVR
    3. Saves benchmark comparison figures
    4. Serializes the SVR champion model to models/
    """
    data_dir = os.path.join(project_root, "data")
    models_dir = os.path.join(project_root, "models")
    assets_dir = os.path.join(project_root, "assets")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "ev_driving_dataset.csv")
    if os.path.exists(csv_path):
        print(f"Loading existing dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
    else:
        print("Generating 5,000 driving trip records based on VED Nissan Leaf dynamics...")
        df = generate_ev_dataset(n_samples=5000, random_seed=42)
        df.to_csv(csv_path, index=False)
        print(f"Dataset saved to {csv_path}")

    feature_cols = [
        "speed_kmh",
        "ambient_temp_c",
        "soc_percent",
        "road_slope_pct",
        "hvac_power_kw",
    ]
    target_col = "remaining_range_km"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Training split: {len(X_train)} samples | Test split: {len(X_test)} samples")

    candidate_models = {
        "Random Forest": RandomForestRegressor(
            n_estimators=150, max_depth=12, min_samples_split=4, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=180, learning_rate=0.08, max_depth=5, subsample=0.85, random_state=42
        ),
        "Support Vector Regressor (SVR)": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("svr", SVR(kernel="rbf", C=100.0, epsilon=1.0)),
            ]
        ),
    }

    metrics_records = {}
    test_predictions = {}

    print("-" * 65)
    print("Beginning Model Benchmarking...")
    print("-" * 65)

    for name, model in candidate_models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        test_predictions[name] = y_pred

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        metrics_records[name] = {
            "MAE (km)": mae,
            "RMSE (km)": rmse,
            "R2 Score": r2,
        }

    results_df = pd.DataFrame(metrics_records).T.sort_values(by="R2 Score", ascending=False)
    print("\n" + "=" * 65)
    print("MODEL BENCHMARK RESULTS")
    print("=" * 65)
    print(
        results_df.to_string(
            formatters={
                "MAE (km)": "{:.2f} km".format,
                "RMSE (km)": "{:.2f} km".format,
                "R2 Score": "{:.4f}".format,
            }
        )
    )
    print("=" * 65)

    # Serialize SVR champion model
    champion_path = os.path.join(models_dir, "svr_pipeline.joblib")
    joblib.dump(candidate_models["Support Vector Regressor (SVR)"], champion_path)
    print(f"\nChampion model (SVR Pipeline) serialized to: {champion_path}")

    # Generate benchmark plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    for ax, (name, y_pred) in zip(axes, test_predictions.items()):
        ax.scatter(y_test, y_pred, alpha=0.35, color="#1e40af", edgecolors="none", s=18)
        min_v = min(y_test.min(), y_pred.min())
        max_v = max(y_test.max(), y_pred.max())
        ax.plot([min_v, max_v], [min_v, max_v], "r--", lw=2, label="Ideal (y=x)")

        mae_val = metrics_records[name]["MAE (km)"]
        r2_val = metrics_records[name]["R2 Score"]
        ax.set_title(f"{name}\nMAE: {mae_val:.2f} km | R2: {r2_val:.4f}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Actual Range (km)", fontsize=10)
        if ax == axes[0]:
            ax.set_ylabel("Predicted Range (km)", fontsize=10)
        ax.legend(loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plot_path = os.path.join(assets_dir, "ev_model_comparison.png")
    plt.savefig(plot_path, dpi=180)
    plt.close()
    print(f"Comparison chart saved to: {plot_path}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, ".."))
    train_and_evaluate(project_root=root_dir)
