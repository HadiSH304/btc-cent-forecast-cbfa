#!/usr/bin/env python3
"""
btc-cent-forecast-01 — 3-feature standardized ridge (lambda=10)
FROZEN constants from OOS-validated model (Nov 7-10 + Nov 13-14)
"""

import json
import os
import glob

# FROZEN CONSTANTS (train = Nov 7-10 pool union + Nov 13-14 race week)
MU = [-12.3, -184.52, -25.64]
SD = [260.14, 571.73, 255.4]
W = [37.55, -115.29, -126.46, -144.04]  # [w1, w2, w3, intercept]

INPUT_DIR = os.environ.get("INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/output")


def compute_forecast(prices: list[float]) -> float:
    """Compute forecast using 3-feature standardized ridge model."""
    n = len(prices)
    if n == 0:
        return 0.0  # empty prices - return minimum valid price
    if n < 361:
        return prices[-1]  # persistence fallback

    x = prices[-1]

    # f1 = x - prices[-31]          # 30-min jump $
    # f2 = x - prices[-361]         # 6-hour drift $
    # f3 = x - mean(prices[-120:])  # gap to 2h mean $
    f1 = x - prices[-31]
    f2 = x - prices[-361]
    f3 = x - (sum(prices[-120:]) / 120.0)

    # Standardize: z = (f - mu) / sd
    z1 = (f1 - MU[0]) / SD[0]
    z2 = (f2 - MU[1]) / SD[1]
    z3 = (f3 - MU[2]) / SD[2]

    # Forecast: x + w1*z1 + w2*z2 + w3*z3 + w4
    forecast = x + W[0] * z1 + W[1] * z2 + W[2] * z3 + W[3]

    # Clamp: round to 5 decimals, then clamp to [0.00001, 9999999.99999]
    forecast = round(forecast, 5)
    if forecast < 0.00001:
        forecast = 0.00001
    elif forecast > 9999999.99999:
        forecast = 9999999.99999

    return forecast


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_files = glob.glob(os.path.join(INPUT_DIR, "*.in"))
    for in_path in input_files:
        case_id = os.path.splitext(os.path.basename(in_path))[0]

        try:
            with open(in_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            # Invalid JSON or unreadable file - write persistence fallback
            forecast = 0.0
            out_path = os.path.join(OUTPUT_DIR, f"{case_id}.out")
            output = {"forecasts": [{"case": case_id, "price": forecast}]}
            with open(out_path, "w") as f:
                json.dump(output, f, separators=(",", ":"))
            continue

        # Extract prices: markets[0].prices with error handling
        try:
            prices = data["markets"][0]["prices"]
            if not isinstance(prices, list):
                raise TypeError
        except (KeyError, IndexError, TypeError):
            # Invalid structure - write persistence fallback
            forecast = 0.0
            out_path = os.path.join(OUTPUT_DIR, f"{case_id}.out")
            output = {"forecasts": [{"case": case_id, "price": forecast}]}
            with open(out_path, "w") as f:
                json.dump(output, f, separators=(",", ":"))
            continue

        # Validate prices are numeric
        try:
            prices = [float(p) for p in prices]
        except (ValueError, TypeError):
            forecast = 0.0
            out_path = os.path.join(OUTPUT_DIR, f"{case_id}.out")
            output = {"forecasts": [{"case": case_id, "price": forecast}]}
            with open(out_path, "w") as f:
                json.dump(output, f, separators=(",", ":"))
            continue

        forecast = compute_forecast(prices)

        out_path = os.path.join(OUTPUT_DIR, f"{case_id}.out")
        output = {"forecasts": [{"case": case_id, "price": forecast}]}

        with open(out_path, "w") as f:
            json.dump(output, f, separators=(",", ":"))


if __name__ == "__main__":
    main()