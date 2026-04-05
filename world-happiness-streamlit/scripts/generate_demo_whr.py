"""Generate data/demo_whr.csv for local/cloud demo when the official Excel is absent."""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "demo_whr.csv"

# Roughly plausible ranges; not official WHR numbers.
SEED = 42
BASE = [
    ("Finland", "FIN", 7.6, 10.8, 5_500_000),
    ("Denmark", "DNK", 7.5, 10.7, 5_800_000),
    ("Iceland", "ISL", 7.4, 10.6, 360_000),
    ("Sweden", "SWE", 7.3, 10.9, 10_300_000),
    ("Norway", "NOR", 7.4, 11.0, 5_400_000),
    ("Netherlands", "NLD", 7.3, 10.9, 17_200_000),
    ("Switzerland", "CHE", 7.5, 11.0, 8_700_000),
    ("Luxembourg", "LUX", 7.2, 11.2, 630_000),
    ("New Zealand", "NZL", 7.2, 10.5, 5_100_000),
    ("Austria", "AUT", 7.2, 10.8, 8_900_000),
    ("Australia", "AUS", 7.1, 10.7, 25_700_000),
    ("Israel", "ISR", 7.1, 10.5, 9_200_000),
    ("Canada", "CAN", 7.0, 10.7, 38_000_000),
    ("Ireland", "IRL", 7.0, 11.0, 5_000_000),
    ("Germany", "DEU", 7.0, 10.8, 83_000_000),
    ("United States", "USA", 6.9, 10.9, 331_000_000),
    ("United Kingdom", "GBR", 6.8, 10.7, 67_000_000),
    ("Czechia", "CZE", 6.9, 10.5, 10_500_000),
    ("Belgium", "BEL", 6.9, 10.7, 11_500_000),
    ("France", "FRA", 6.7, 10.6, 67_000_000),
    ("Spain", "ESP", 6.5, 10.4, 47_000_000),
    ("Italy", "ITA", 6.4, 10.4, 59_000_000),
    ("Portugal", "PRT", 6.2, 10.3, 10_300_000),
    ("Poland", "POL", 6.1, 10.2, 38_000_000),
    ("Japan", "JPN", 5.9, 10.5, 125_000_000),
    ("South Korea", "KOR", 5.9, 10.5, 51_000_000),
    ("Brazil", "BRA", 6.3, 9.8, 214_000_000),
    ("Mexico", "MEX", 6.4, 9.9, 128_000_000),
    ("Argentina", "ARG", 5.9, 9.7, 45_000_000),
    ("Chile", "CHL", 6.2, 10.0, 19_000_000),
    ("South Africa", "ZAF", 5.5, 9.5, 59_000_000),
    ("India", "IND", 4.0, 8.8, 1_400_000_000),
    ("China", "CHN", 5.5, 9.5, 1_400_000_000),
    ("Russia", "RUS", 5.5, 10.0, 144_000_000),
    ("Turkey", "TUR", 5.4, 9.8, 84_000_000),
    ("Egypt", "EGY", 4.2, 9.0, 102_000_000),
    ("Nigeria", "NGA", 4.6, 8.7, 213_000_000),
    ("Kenya", "KEN", 4.5, 8.5, 53_000_000),
    ("Afghanistan", "AFG", 2.4, 7.5, 38_000_000),
]


def main() -> None:
    random.seed(SEED)
    rows = []
    years = list(range(2010, 2024))
    for country, iso, h0, gdp0, pop in BASE:
        for y in years:
            t = (y - 2010) / 13
            noise = random.uniform(-0.12, 0.12)
            h = h0 + 0.15 * t + noise
            gdp = gdp0 + 0.08 * t + random.uniform(-0.05, 0.05)
            rows.append(
                {
                    "Country": country,
                    "Year": y,
                    "Happiness": round(max(1.5, min(8.2, h)), 3),
                    "GDP": round(max(7.0, min(12.0, gdp)), 3),
                    "SocialSupport": round(random.uniform(0.75, 0.98), 3),
                    "HealthyLifeExpectancy": round(random.uniform(62, 82), 1),
                    "Freedom": round(random.uniform(0.55, 0.95), 3),
                    "Corruption": round(random.uniform(0.15, 0.85), 3),
                    "Generosity": round(random.uniform(-0.05, 0.25), 3),
                    "Population": pop,
                    "iso_a3": iso,
                }
            )
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} rows to {OUT}")


if __name__ == "__main__":
    main()
