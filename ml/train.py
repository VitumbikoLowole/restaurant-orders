"""
Train and save the two ML models:
  1. RandomForestRegressor  → predicted orders per hour  (volume)
  2. RandomForestClassifier → Peak / No-Peak label       (period)

Run via Django management command:
    python manage.py train_ml_models

Or directly (with DJANGO_SETTINGS_MODULE set):
    python -m ml.train
"""

import json
import math
import pathlib

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

from ml.data_generator import generate

SAVE_DIR = pathlib.Path(__file__).parent / "saved_models"

FEATURE_COLS = [
    "hour_of_day", "day_of_week", "is_weekend",
    "month", "week_of_year",
    "is_lunch_hour", "is_dinner_hour",
    "temperature_c", "is_raining", "rainfall_mm",
    "is_public_holiday", "is_school_holiday",
    "lag_1d_orders", "lag_7d_orders", "rolling_7d_avg",
]

# Slot averages at or above the 70th percentile → Peak
PEAK_PERCENTILE = 70


def _add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["lag_1d_orders"]  = df["orders"].shift(24)
    df["lag_7d_orders"]  = df["orders"].shift(168)
    df["rolling_7d_avg"] = (
        df["orders"].shift(1).rolling(window=168, min_periods=24).mean()
    )
    return df.dropna(subset=FEATURE_COLS).reset_index(drop=True)


def train_and_save(stdout=None) -> dict:
    def log(msg: str):
        if stdout:
            stdout.write(msg)
        else:
            print(msg)

    log("Generating 2-year synthetic dataset …")
    df = pd.DataFrame(generate(seed=42))
    df = _add_lag_features(df)
    log(f"  {len(df):,} usable rows (after dropping lag warm-up)")

    # Chronological 80 / 20 split — no data leakage
    split = int(len(df) * 0.80)
    train_df, test_df = df.iloc[:split].copy(), df.iloc[split:].copy()

    X_train = train_df[FEATURE_COLS]
    y_train = train_df["orders"]
    X_test  = test_df[FEATURE_COLS]
    y_test  = test_df["orders"]

    log("Fitting StandardScaler on training set …")
    scaler       = StandardScaler()
    X_train_s    = scaler.fit_transform(X_train)
    X_test_s     = scaler.transform(X_test)

    # ── 1. Volume regressor ──────────────────────────────────────────────────
    log("Training RandomForestRegressor (order volume) …")
    vol_model = RandomForestRegressor(
        n_estimators=100, max_depth=12, random_state=42, n_jobs=-1
    )
    vol_model.fit(X_train_s, y_train)
    y_pred_vol = vol_model.predict(X_test_s)

    mae  = float(mean_absolute_error(y_test, y_pred_vol))
    r2   = float(r2_score(y_test, y_pred_vol))
    rmse = float(math.sqrt(((y_test.values - y_pred_vol) ** 2).mean()))
    log(f"  Volume  ->  MAE={mae:.3f}  RMSE={rmse:.3f}  R2={r2:.3f}")

    # ── 2. Peak threshold via training-set slot averages ────────────────────
    slot_avg = (
        train_df.groupby(["day_of_week", "hour_of_day"])["orders"].mean()
    )
    peak_threshold = float(np.percentile(slot_avg.values, PEAK_PERCENTILE))
    log(f"  Peak threshold ({PEAK_PERCENTILE}th pct of slot averages): {peak_threshold:.2f} orders/hr")

    y_train_peak = (train_df["orders"] >= peak_threshold).astype(int)
    y_test_peak  = (test_df["orders"]  >= peak_threshold).astype(int)

    # ── 3. Peak classifier ──────────────────────────────────────────────────
    log("Training RandomForestClassifier (peak period) …")
    peak_model = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42,
        n_jobs=-1, class_weight="balanced"
    )
    peak_model.fit(X_train_s, y_train_peak)
    y_pred_peak = peak_model.predict(X_test_s)

    acc = float(accuracy_score(y_test_peak, y_pred_peak))
    f1  = float(f1_score(y_test_peak, y_pred_peak))
    log(f"  Peak    ->  Accuracy={acc:.3f}  F1={f1:.3f}")

    # ── Feature importance (top 5) ──────────────────────────────────────────
    importances = sorted(
        zip(FEATURE_COLS, vol_model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )[:5]
    log("  Top-5 features: " + ", ".join(f"{n}={v:.3f}" for n, v in importances))

    # ── Save artefacts ───────────────────────────────────────────────────────
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vol_model,  SAVE_DIR / "volume_model.pkl")
    joblib.dump(peak_model, SAVE_DIR / "peak_model.pkl")
    joblib.dump(scaler,     SAVE_DIR / "scaler.pkl")

    meta = {
        "feature_cols":    FEATURE_COLS,
        "peak_threshold":  peak_threshold,
        "peak_percentile": PEAK_PERCENTILE,
        "metrics": {
            "volume_mae":  round(mae, 3),
            "volume_rmse": round(rmse, 3),
            "volume_r2":   round(r2, 3),
            "peak_acc":    round(acc, 3),
            "peak_f1":     round(f1, 3),
        },
        "top_features": [{"name": n, "importance": round(v, 4)} for n, v in importances],
    }
    with open(SAVE_DIR / "meta.json", "w") as fh:
        json.dump(meta, fh, indent=2)

    log(f"Artefacts saved to {SAVE_DIR}")
    return meta


if __name__ == "__main__":
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant_orders.settings")
    django.setup()
    train_and_save()
