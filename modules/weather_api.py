"""
weather_api.py
----------------
Uses the free OpenWeatherMap API (https://openweathermap.org/api) for:
  1. Hyperlocal 5-day weather alerts (rain / heat / frost warnings)
  2. Supplying live rainfall + temperature + humidity to the soil
     moisture advisor, so the farmer doesn't need a rain gauge.

SETUP
-----
1. Create a free account at openweathermap.org -> get an API key
   (free tier allows 1,000 calls/day - plenty for a hackathon demo).
2. Set it as an environment variable before running the Flask app:
       export OPENWEATHER_API_KEY="your_key_here"     (Mac/Linux)
       set OPENWEATHER_API_KEY=your_key_here           (Windows)
3. If no key is set, this module returns realistic MOCK data so the
   rest of the demo still works offline / without a key.
"""

import os
from datetime import datetime, timedelta

import requests

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

HEAT_THRESHOLD_C = 38
FROST_THRESHOLD_C = 4
RAIN_THRESHOLD_MM = 10


def _mock_forecast(location_name):
    """Offline fallback so the demo works with no internet / no API key."""
    today = datetime.now()
    days = []
    sample = [
        {"temp": 34, "humidity": 55, "rain_mm": 0},
        {"temp": 39, "humidity": 40, "rain_mm": 0},
        {"temp": 31, "humidity": 78, "rain_mm": 18},
        {"temp": 29, "humidity": 82, "rain_mm": 22},
        {"temp": 33, "humidity": 60, "rain_mm": 2},
    ]
    for i, d in enumerate(sample):
        days.append({
            "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
            "temperature_c": d["temp"],
            "humidity_pct": d["humidity"],
            "rainfall_mm": d["rain_mm"],
        })
    return {"location": location_name, "source": "mock (no API key set)", "days": days}


def get_forecast(location_name):
    """Returns a 5-day simplified forecast for the given place name."""
    if not API_KEY:
        return _mock_forecast(location_name)

    try:
        geo_resp = requests.get(
            GEOCODE_URL, params={"q": location_name, "limit": 1, "appid": API_KEY}, timeout=8
        ).json()
        if not geo_resp:
            return {"error": f"Location '{location_name}' not found."}

        lat, lon = geo_resp[0]["lat"], geo_resp[0]["lon"]

        forecast_resp = requests.get(
            FORECAST_URL,
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"},
            timeout=8,
        ).json()

        # OpenWeather's free "forecast" endpoint returns 3-hour steps for 5 days;
        # we collapse these into one summary row per day.
        daily = {}
        for entry in forecast_resp.get("list", []):
            date = entry["dt_txt"].split(" ")[0]
            daily.setdefault(date, {"temps": [], "humidity": [], "rain": 0.0})
            daily[date]["temps"].append(entry["main"]["temp"])
            daily[date]["humidity"].append(entry["main"]["humidity"])
            daily[date]["rain"] += entry.get("rain", {}).get("3h", 0.0)

        days = []
        for date, vals in list(daily.items())[:5]:
            days.append({
                "date": date,
                "temperature_c": round(sum(vals["temps"]) / len(vals["temps"]), 1),
                "humidity_pct": round(sum(vals["humidity"]) / len(vals["humidity"]), 1),
                "rainfall_mm": round(vals["rain"], 1),
            })

        return {"location": location_name, "source": "openweathermap", "days": days}

    except requests.RequestException as e:
        # network unavailable in the field -> fall back to mock so the
        # farmer-facing screen never just shows a blank error
        fallback = _mock_forecast(location_name)
        fallback["source"] = f"mock (network error: {e})"
        return fallback


def build_alerts(forecast):
    """Turns raw numbers into simple alert flags a farmer can act on."""
    alerts = []
    for day in forecast.get("days", []):
        flags = []
        if day["rainfall_mm"] >= RAIN_THRESHOLD_MM:
            flags.append("rain_alert")
        if day["temperature_c"] >= HEAT_THRESHOLD_C:
            flags.append("heat_alert")
        if day["temperature_c"] <= FROST_THRESHOLD_C:
            flags.append("frost_alert")
        alerts.append({"date": day["date"], "flags": flags or ["normal_weather"]})
    return alerts


def get_recent_rainfall_mm(location_name):
    """
    Convenience helper for soil_moisture_predictor: returns an approximate
    'rainfall in the last 3 days' figure and today's temp/humidity, pulled
    from the same forecast data (used as a proxy since historical rainfall
    needs a paid API tier).
    """
    forecast = get_forecast(location_name)
    days = forecast.get("days", [])
    if not days:
        return {"temperature_c": 30.0, "humidity_pct": 60.0, "rainfall_mm_last_3d": 0.0}

    today = days[0]
    rainfall_sum = sum(d["rainfall_mm"] for d in days[:3])
    return {
        "temperature_c": today["temperature_c"],
        "humidity_pct": today["humidity_pct"],
        "rainfall_mm_last_3d": round(rainfall_sum, 1),
    }
