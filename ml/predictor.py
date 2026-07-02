"""
Load trained artefacts and return hourly forecasts for any date.

Usage (inside a Django view or shell)
--------------------------------------
    from ml.predictor import get_predictions
    forecast = get_predictions()      # today + tomorrow
    forecast = get_predictions(base_date=some_date)
"""

import datetime
import json
import pathlib
import random
from typing import Optional

import joblib
import numpy as np
import pandas as pd

from ml.data_generator import (
    DAY_MULTIPLIER,
    HOURLY_BASE,
    is_public_holiday,
    is_school_holiday,
    simulate_weather,
)

SAVE_DIR = pathlib.Path(__file__).parent / "saved_models"

# Module-level cache so models are loaded once per process
_CACHE: dict = {}


def _load() -> dict:
    if _CACHE:
        return _CACHE
    if not (SAVE_DIR / "meta.json").exists():
        raise FileNotFoundError(
            "ML models not found. Run: python manage.py train_ml_models"
        )
    with open(SAVE_DIR / "meta.json") as fh:
        meta = json.load(fh)
    _CACHE["vol_model"]  = joblib.load(SAVE_DIR / "volume_model.pkl")
    _CACHE["peak_model"] = joblib.load(SAVE_DIR / "peak_model.pkl")
    _CACHE["scaler"]     = joblib.load(SAVE_DIR / "scaler.pkl")
    _CACHE["meta"]       = meta
    return _CACHE


def _real_lag_orders(date: datetime.date) -> float:
    """
    Query the live DB for average daily orders over the 7 days before *date*.
    Returns 0.0 gracefully on any error (e.g. models not wired to DB yet).
    """
    try:
        import datetime as dt_mod
        from django.utils import timezone
        from menu.models import Order

        tz = timezone.get_current_timezone()
        period_end   = timezone.make_aware(
            dt_mod.datetime.combine(date - dt_mod.timedelta(days=1), dt_mod.time.max), tz
        )
        period_start = timezone.make_aware(
            dt_mod.datetime.combine(date - dt_mod.timedelta(days=7), dt_mod.time.min), tz
        )
        count = Order.objects.filter(
            created_at__range=(period_start, period_end)
        ).count()
        return count / 7.0
    except Exception:
        return 0.0


def _build_feature_matrix(
    date: datetime.date,
    temperature_c: Optional[float] = None,
    is_raining: Optional[bool] = None,
    rainfall_mm: Optional[float] = None,
    is_public_holiday_flag: Optional[bool] = None,
    is_school_holiday_flag: Optional[bool] = None,
) -> np.ndarray:
    """
    Return shape (24, 15) feature matrix — one row per hour.

    Weather and event parameters default to simulated/auto-detected values
    when not supplied.  Pass them explicitly for user-driven predictions.
    """
    rng = random.Random(date.toordinal())
    sim_temp, sim_raining, sim_rainfall = simulate_weather(date, rng)

    temp       = temperature_c if temperature_c is not None else sim_temp
    raining    = is_raining    if is_raining    is not None else sim_raining
    rainfall   = rainfall_mm   if rainfall_mm   is not None else sim_rainfall
    is_pub     = is_public_holiday_flag  if is_public_holiday_flag  is not None else is_public_holiday(date)
    is_sch     = is_school_holiday_flag  if is_school_holiday_flag  is not None else is_school_holiday(date)

    dow     = date.weekday()
    month   = date.month
    week    = date.isocalendar()[1]
    rolling = _real_lag_orders(date)

    rows = []
    for hour in range(24):
        slot_base = HOURLY_BASE[hour] * DAY_MULTIPLIER[dow]
        rows.append([
            hour,
            dow,
            int(dow >= 5),
            month,
            week,
            int(11 <= hour <= 14),
            int(18 <= hour <= 21),
            temp,
            int(raining),
            rainfall,
            int(is_pub),
            int(is_sch),
            slot_base,
            slot_base,
            rolling,
        ])
    return np.array(rows, dtype=float)


def predict_day(
    date: datetime.date,
    temperature_c: Optional[float] = None,
    is_raining: Optional[bool] = None,
    rainfall_mm: Optional[float] = None,
    is_public_holiday_flag: Optional[bool] = None,
    is_school_holiday_flag: Optional[bool] = None,
) -> list:
    """
    Return a list of 24 dicts, one per hour:
        hour, label, predicted_orders, is_peak, peak_prob
    """
    loaded       = _load()
    feature_cols = loaded["meta"]["feature_cols"]
    X  = pd.DataFrame(
        _build_feature_matrix(
            date,
            temperature_c=temperature_c,
            is_raining=is_raining,
            rainfall_mm=rainfall_mm,
            is_public_holiday_flag=is_public_holiday_flag,
            is_school_holiday_flag=is_school_holiday_flag,
        ),
        columns=feature_cols,
    )
    X_s = loaded["scaler"].transform(X)

    volumes    = loaded["vol_model"].predict(X_s)
    peak_probs = loaded["peak_model"].predict_proba(X_s)[:, 1]
    peak_flags = loaded["peak_model"].predict(X_s)

    return [
        {
            "hour":             h,
            "label":            f"{h:02d}:00",
            "predicted_orders": max(0, int(round(float(volumes[h])))),
            "is_peak":          bool(peak_flags[h]),
            "peak_prob":        round(float(peak_probs[h]), 3),
        }
        for h in range(24)
    ]


def _peak_windows(hours: list) -> list:
    """Convert a list of hourly dicts into consecutive peak windows."""
    windows, in_peak, start = [], False, None
    for h in hours:
        if h["is_peak"] and not in_peak:
            in_peak, start = True, h["hour"]
        elif not h["is_peak"] and in_peak:
            windows.append({"start": start, "end": h["hour"] - 1,
                            "label": f"{start:02d}:00-{h['hour']-1:02d}:59"})
            in_peak = False
    if in_peak:
        windows.append({"start": start, "end": 23,
                        "label": f"{start:02d}:00-23:59"})
    return windows


def _staffing_for(predicted_orders: int) -> int:
    """Simple rule-of-thumb: orders/hour → minimum staff needed."""
    if predicted_orders >= 10:
        return 4
    if predicted_orders >= 7:
        return 3
    if predicted_orders >= 3:
        return 2
    return 1


def get_predictions(base_date: Optional[datetime.date] = None) -> dict:
    """
    Return a combined forecast dict with today's and tomorrow's predictions,
    staffing recommendations, and model performance metrics.
    """
    from django.utils import timezone

    today    = base_date or timezone.localdate()
    tomorrow = today + datetime.timedelta(days=1)

    today_hours    = predict_day(today)
    tomorrow_hours = predict_day(tomorrow)

    meta = _load()["meta"]

    def enrich(hours):
        for h in hours:
            h["staff_needed"] = _staffing_for(h["predicted_orders"])
        return hours

    today_hours    = enrich(today_hours)
    tomorrow_hours = enrich(tomorrow_hours)

    return {
        "today": {
            "date":         today,
            "date_label":   today.strftime("%A, %d %b %Y"),
            "hours":        today_hours,
            "peaks":        _peak_windows(today_hours),
            "total_predicted": sum(h["predicted_orders"] for h in today_hours),
            "peak_count":   sum(1 for h in today_hours if h["is_peak"]),
        },
        "tomorrow": {
            "date":         tomorrow,
            "date_label":   tomorrow.strftime("%A, %d %b %Y"),
            "hours":        tomorrow_hours,
            "peaks":        _peak_windows(tomorrow_hours),
            "total_predicted": sum(h["predicted_orders"] for h in tomorrow_hours),
            "peak_count":   sum(1 for h in tomorrow_hours if h["is_peak"]),
        },
        "metrics":         meta["metrics"],
        "top_features":    meta.get("top_features", []),
        "peak_threshold":  meta["peak_threshold"],
        "peak_percentile": meta["peak_percentile"],
    }
