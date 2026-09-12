"""
soil_moisture_estimator.py
----------------------------
IMPORTANT HONESTY NOTE
-----------------------
A weather API (rainfall/temperature/humidity/forecast) does NOT measure
soil moisture. Real soil moisture needs a physical capacitive/resistive
sensor in the ground, or paid satellite remote-sensing data.

This module produces an **Estimated Soil Moisture** value using a simple,
transparent daily water-balance heuristic:

    moisture[day] = moisture[day-1] + effective_rainfall - evapotranspiration

  - effective_rainfall: a portion of the day's rainfall that actually
    infiltrates and is retained near the root zone (capped, since heavy
    rain mostly runs off/drains rather than linearly raising moisture).
  - evapotranspiration (ET): a rough proxy driven by temperature and
    humidity (hotter + drier air pulls more moisture out of the soil).

This is a domain heuristic for demo/advisory purposes, NOT a calibrated
agronomic model and NOT a sensor reading. It is always labeled
"Estimated Soil Moisture" end-to-end (API response keys, UI text,
translations) so nobody mistakes it for a measurement.
"""

BASELINE_MOISTURE_PCT = 50.0  # neutral starting assumption; no sensor history exists
RAINFALL_INFILTRATION_CAP_MM = 25.0  # rain beyond this per day mostly runs off
RAINFALL_TO_MOISTURE_FACTOR = 0.7    # % moisture gained per effective mm of rain
MIN_MOISTURE, MAX_MOISTURE = 5.0, 95.0


def _daily_et_proxy(temperature_c, humidity_pct):
    """
    Rough evapotranspiration-style proxy (NOT the real Penman-Monteith/
    Hargreaves equation - a simplified stand-in appropriate for a
    hackathon-level advisory heuristic).
    """
    heat_component = max(0.0, (temperature_c - 22.0)) * 0.55
    dryness_component = max(0.0, (100.0 - humidity_pct)) * 0.12
    return heat_component + dryness_component


def estimate_series(days, initial_moisture_pct=BASELINE_MOISTURE_PCT):
    """
    days: list of {date, temperature_c, humidity_pct, rainfall_mm} from
    weather_api.get_forecast(), in chronological order.

    Returns the same list of dicts with an added
    'estimated_soil_moisture_pct' key (rounded to 1 decimal), plus a
    'trend' key on the whole run isn't included here - callers can
    compare first/last values for that.
    """
    moisture = initial_moisture_pct
    enriched = []
    for day in days:
        effective_rain = min(day.get("rainfall_mm", 0.0), RAINFALL_INFILTRATION_CAP_MM)
        et = _daily_et_proxy(day.get("temperature_c", 30.0), day.get("humidity_pct", 55.0))
        moisture = moisture + (effective_rain * RAINFALL_TO_MOISTURE_FACTOR) - et
        moisture = max(MIN_MOISTURE, min(MAX_MOISTURE, moisture))

        enriched_day = dict(day)
        enriched_day["estimated_soil_moisture_pct"] = round(moisture, 1)
        enriched.append(enriched_day)
    return enriched
