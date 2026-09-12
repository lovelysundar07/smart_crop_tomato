"""
generate_soil_moisture_dataset.py
-----------------------------------
HONESTY NOTE: No real sensor-labeled irrigation dataset exists for this
project. This script generates a SYNTHETIC training set using an
explicit, documented agronomic rule (below) plus random noise, so the
Random Forest has something meaningful and reproducible to learn from
for a hackathon demo.

This is a reasonable and common approach when no labeled field data is
available yet - but it should be described honestly as synthetic/
rule-derived training data, not real farm sensor data, in any
presentation of this project.

LABELING RULE (irrigation_label)
---------------------------------
We score "irrigation need" from four physically-motivated factors:
  1. Low estimated soil moisture -> higher need
  2. Low humidity -> higher need (faster drying)
  3. High temperature -> higher need (more evapotranspiration)
  4. Little/no rainfall today -> higher need
  5. Growth stage modifies sensitivity (seedlings & flowering/fruiting
     need more consistent moisture than the vegetative stage)
  6. Soil type modifies how fast moisture is lost (sandy drains faster,
     clay retains longer)

The weighted score is bucketed into LOW / MEDIUM / HIGH, then ~8% label
noise is added to avoid an unrealistically perfect/overfit model.

Run:  python data/generate_soil_moisture_dataset.py
Output: data/soil_moisture_dataset.csv
"""

import os
import random

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

N_SAMPLES = 6000

SOIL_TYPES = ["sandy", "loamy", "clay"]
SOIL_DRAIN_FACTOR = {"sandy": 1.25, "loamy": 1.0, "clay": 0.75}  # higher = dries faster

GROWTH_STAGES = ["seedling", "vegetative", "flowering", "fruiting"]
STAGE_SENSITIVITY = {"seedling": 1.3, "vegetative": 1.0, "flowering": 1.2, "fruiting": 1.25}


def label_row(temperature_c, humidity_pct, rainfall_mm, estimated_soil_moisture_pct,
              soil_type, growth_stage):
    dryness_score = (100 - estimated_soil_moisture_pct) / 100.0          # 0..1, higher = drier
    humidity_score = (100 - humidity_pct) / 100.0                         # 0..1, higher = drier air
    heat_score = max(0.0, (temperature_c - 24)) / 20.0                    # 0..~1
    rain_relief = min(rainfall_mm, 20.0) / 20.0                           # 0..1, higher = less need

    raw = (
        dryness_score * 0.45
        + humidity_score * 0.20
        + heat_score * 0.20
        - rain_relief * 0.35
    )
    raw *= SOIL_DRAIN_FACTOR[soil_type]
    raw *= STAGE_SENSITIVITY[growth_stage]

    # small amount of label noise so the model doesn't learn a trivial threshold
    raw += np.random.normal(0, 0.05)

    if raw < 0.28:
        return "LOW"
    elif raw < 0.55:
        return "MEDIUM"
    else:
        return "HIGH"


def generate():
    rows = []
    for _ in range(N_SAMPLES):
        temperature_c = np.random.uniform(18, 42)
        humidity_pct = np.random.uniform(25, 95)
        rainfall_mm = np.random.choice(
            [0, 0, 0, np.random.uniform(0.5, 5), np.random.uniform(5, 15), np.random.uniform(15, 40)],
            p=[0.35, 0.15, 0.1, 0.2, 0.13, 0.07],
        )
        estimated_soil_moisture_pct = np.clip(
            np.random.normal(50, 18) + rainfall_mm * 0.8 - max(0, temperature_c - 25) * 0.6, 5, 95
        )
        soil_type = random.choice(SOIL_TYPES)
        growth_stage = random.choice(GROWTH_STAGES)

        label = label_row(temperature_c, humidity_pct, rainfall_mm,
                           estimated_soil_moisture_pct, soil_type, growth_stage)

        rows.append({
            "temperature_c": round(temperature_c, 1),
            "humidity_pct": round(humidity_pct, 1),
            "rainfall_mm": round(rainfall_mm, 1),
            "estimated_soil_moisture_pct": round(estimated_soil_moisture_pct, 1),
            "soil_type": soil_type,
            "growth_stage": growth_stage,
            "irrigation_label": label,
        })

    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(__file__), "soil_moisture_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    print(df["irrigation_label"].value_counts())


if __name__ == "__main__":
    generate()
