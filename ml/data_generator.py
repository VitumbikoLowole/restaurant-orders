"""
Synthetic hourly restaurant demand dataset for Rwanda (Kigali).

Covers 2024-01-01 00:00 to 2025-12-31 23:00 (17 520 rows).
Each row = one hour.  Target column: ``orders`` (integer count).

Usage
-----
    from ml.data_generator import generate
    records = generate(seed=42)   # list[dict]
"""

import datetime
import random
from typing import Any, Dict, List

# ── Bimodal demand curve for an average Tuesday (orders/hour) ────────────────
HOURLY_BASE: Dict[int, float] = {
    0: 0.0,  1: 0.0,  2: 0.0,  3: 0.0,  4: 0.0,  5: 0.0,
    6: 0.0,  7: 0.8,  8: 1.5,  9: 2.5, 10: 4.0, 11: 7.0,
    12: 11.0, 13: 12.0, 14: 9.0, 15: 5.0, 16: 4.0, 17: 6.0,
    18: 9.0, 19: 12.0, 20: 11.0, 21: 8.0, 22: 4.0, 23: 1.5,
}

# Weekday demand multiplier: Mon=0 … Sun=6
DAY_MULTIPLIER = [0.70, 0.75, 0.80, 0.85, 1.00, 1.30, 1.15]

# Rwanda rainy seasons: March–May, October–November
RAINY_MONTHS = {3, 4, 5, 10, 11}

# Rwanda public holidays: (month, day) → label
PUBLIC_HOLIDAYS = {
    (1,  1): "New Year's Day",
    (2,  1): "Heroes Day",
    (4,  7): "Genocide Memorial",
    (5,  1): "Labour Day",
    (7,  1): "Independence Day",
    (7,  4): "Liberation Day",
    (8, 15): "Assumption",
    (12, 25): "Christmas Day",
    (12, 26): "Boxing Day",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def _umuganura(year: int) -> datetime.date:
    """First Friday of August in the given year."""
    d = datetime.date(year, 8, 1)
    offset = (4 - d.weekday()) % 7   # Friday = weekday 4
    return d + datetime.timedelta(days=offset)


def is_public_holiday(dt: datetime.date) -> bool:
    if (dt.month, dt.day) in PUBLIC_HOLIDAYS:
        return True
    return dt == _umuganura(dt.year)


def is_school_holiday(dt: datetime.date) -> bool:
    """Rwanda long break: Jul–Aug; Christmas break: 20 Dec – 15 Jan."""
    if dt.month in (7, 8):
        return True
    if dt.month == 12 and dt.day >= 20:
        return True
    if dt.month == 1 and dt.day <= 15:
        return True
    return False


def simulate_weather(dt: datetime.date, rng: random.Random):
    """Return (temperature_c, is_raining, rainfall_mm) for a date."""
    if dt.month in RAINY_MONTHS:
        temp = rng.gauss(19.0, 2.0)
        rain_prob = 0.40
    else:
        temp = rng.gauss(22.0, 2.0)
        rain_prob = 0.10

    temp = round(max(14.0, min(28.0, temp)), 1)
    is_raining = rng.random() < rain_prob
    rainfall_mm = round(rng.expovariate(1 / 12), 1) if is_raining else 0.0
    return temp, is_raining, rainfall_mm


# ── main generator ────────────────────────────────────────────────────────────

def generate(seed: int = 42) -> List[Dict[str, Any]]:
    """
    Return a list of hourly records spanning 2024-01-01 to 2025-12-31.

    Each dict contains 15 feature columns plus the target ``orders``.
    """
    rng = random.Random(seed)
    start = datetime.datetime(2024, 1, 1, 0, 0)
    end   = datetime.datetime(2025, 12, 31, 23, 0)

    records: List[Dict[str, Any]] = []
    weather_cache: Dict[datetime.date, tuple] = {}

    current = start
    while current <= end:
        date = current.date()

        if date not in weather_cache:
            weather_cache[date] = simulate_weather(date, rng)
        temp, is_raining, rainfall_mm = weather_cache[date]

        hour      = current.hour
        dow       = current.weekday()   # 0 = Monday
        is_pub_h  = is_public_holiday(date)
        is_sch_h  = is_school_holiday(date)

        base         = HOURLY_BASE[hour]
        day_mult     = DAY_MULTIPLIER[dow]
        weather_mult = 0.65 if is_raining else 1.0
        holiday_mult = 1.30 if is_pub_h else (1.15 if is_sch_h else 1.0)
        noise        = max(0.4, min(2.0, rng.gauss(1.0, 0.15)))
        orders       = max(0, round(base * day_mult * weather_mult * holiday_mult * noise))

        records.append({
            "timestamp":         current,
            "hour_of_day":       hour,
            "day_of_week":       dow,
            "is_weekend":        int(dow >= 5),
            "month":             date.month,
            "week_of_year":      date.isocalendar()[1],
            "is_lunch_hour":     int(11 <= hour <= 14),
            "is_dinner_hour":    int(18 <= hour <= 21),
            "temperature_c":     temp,
            "is_raining":        int(is_raining),
            "rainfall_mm":       rainfall_mm,
            "is_public_holiday": int(is_pub_h),
            "is_school_holiday": int(is_sch_h),
            "orders":            orders,
        })
        current += datetime.timedelta(hours=1)

    return records
