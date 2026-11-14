# btc-cent-forecast-01 — FINAL MODEL SPEC v2 (OOS-validated across 2 regimes)

## Validation summary (Nov 14)
- Train Nov 7-10 → OOS test Nov 13-14 (race-week crash): +25.7% vs persistence
- Train race-week → test calm-week: +3.3% (edge holds both directions)
- Walk-forward on Nov 7-10: +11.1%
- Combined-2-regime model FROZEN below (best guess for unseen final window)

## Model: 3-feature standardized ridge (lambda=10), linear, deterministic
features (x = last close of prices, prices = 4320 one-minute closes):
  f1 = x - prices[-31]          # 30-min jump $
  f2 = x - prices[-361]         # 6-hour drift $
  f3 = x - mean(prices[-120:])  # gap to 2h mean $
z = (f - mu)/sd per feature; forecast = x + w1*z1 + w2*z2 + w3*z3 + w4

## FROZEN CONSTANTS (train = Nov 7-10 pool union + Nov 13-14 race week)
mu = [-12.3, -184.52, -25.64]
sd = [260.14, 571.73, 255.4]
w  = [37.55, -115.29, -126.46, -144.04]   # [w1,w2,w3,intercept]

## main.py requirements (Python 3.13)
- read every /input/<id>.in (JSON: markets[0].prices list of floats)
- len(prices) < 361 → fallback forecast = prices[-1] (persistence)
- forecast = clamp(round(x + w1*(f1-mu1)/sd1 + w2*(f2-mu2)/sd2 + w3*(f3-mu3)/sd3 + w4, 5), 0.00001, 9999999.99999)
- write /output/<id>.out exactly: {"forecasts":[{"case":"<id>","price":<forecast>}]}
- stdlib only (json, os, glob), no network, deterministic, <8s

## Process constraints (make.fun gate — MANDATORY)
- repo created AFTER window opens 20:00 UTC Nov 14, github.com/HadiSH304/<new-repo>, OSI license (MIT)
- main.py must take final content from >= 2 assistant messages (fresh claude-code session, in window)
- bundle with kit CLI; quota 1 submission/day → submit once, only when grade-local beats persistence on practice
