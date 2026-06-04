# Meeting brief — Amelia Fox, 2026-06-04 @ 2:00pm CT

Re: `DataforElnino.xlsx` (cleaned ENSO / NAO / sunspot data for the el-niño-26 correlation model)

---

## 1. What she delivered (data inventory)

| Sheet | Variable | Cadence | Range | Notes |
|---|---|---|---|---|
| **ENSO** | ONI (Niño 3.4 anomaly) | Monthly, 12 overlapping 3-mo seasons | 1950 – 2026 (DJF only for 2026) | Cols A–M are the raw ONI; cols O–V are her **pre-aggregated** JFM/AMJ/JAS/OND seasonal means + an annual average. Clean. |
| **NAO** | NAOI | Monthly | Jan 1950 – **Apr 2026** | One value/month, tidy date column. Most up-to-date series. |
| **Sunspots** | Sunspot number | Monthly | 1950 – **2025** | Source: UMass Lowell (`ulcar.uml.edu`). Ends Dec 2025. |
| **credits** | sources | — | — | Sunspots + NAO links present. **ENSO, Weather, USDA Crops rows are blank** — no source URL. |

## 2. Three things to flag on the call (data quality)

1. **Series end on different dates.** NAO runs to Apr 2026, sunspots only to Dec 2025, ENSO 2026 is DJF only. Any merged model is currently capped at **2025** for a complete row. → Ask: can she keep sunspots current, or settle on a fixed cutoff?
2. **Missing source citations.** The `credits` sheet has no URL for **ENSO**, and the *Weather* and *USDA Crops* rows are placeholders. → The ENSO ONI source is confirmed (it matches NOAA CPC ONI v5 to the decimal): **`https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt`** — give her that to drop into the blank credit row. Ask whether *Weather* and *USDA Crops* are still coming.
3. **Pre-aggregated ENSO columns.** She's already computed seasonal + annual ENSO means (cols O–V). Confirm we standardize on *her* aggregation so our numbers match hers — spot-checked one (1950 JFM = -1.333) and it ties out.

## 3. The analytical headline (run on her data, 1950–2025, n=76)

Reproducible via `python src/seasonal_diagnostics.py --xlsx DataforElnino.xlsx` → `results/seasonal_lag_correlation.csv`.

**3a. Raw annual linear correlations with ONI are weak — this is the key modeling conversation.**

| Predictor | Contemporaneous r vs ONI | Best lagged r |
|---|---|---|
| Sunspots | +0.12 | **+0.25–0.26** (leads ONI by 1–2 yr) |
| NAO (annual) | +0.04 | nothing stable |
| NAO (DJF winter) | −0.02 | nothing stable |

**3b. Seasonal matrix — predictor season (year Y) vs ENSO OND (peak season, year Y):**

| Predictor season | Sunspot → OND | NAO → OND |
|---|---|---|
| JFM | +0.14 | +0.05 |
| AMJ | +0.13 | +0.15 |
| JAS | +0.09 | −0.05 |
| OND | +0.07 | **+0.16** |

Best sunspot signal is **JFM sunspots leading ENSO OND by 1 yr: r = +0.16**. NAO's only non-trivial pull is contemporaneous autumn (OND→OND, +0.16) — i.e. ENSO driving NAO, not the reverse, so weak as a *predictor*.

**3c. The dominant signal is ENSO's own persistence — and the spring barrier:**

| ONI season (Y) → ONI OND (Y) | r |
|---|---|
| JFM → OND | **−0.02** ← spring predictability barrier |
| AMJ → OND | **+0.62** |
| JAS → OND | **+0.96** |

**Implication for the model — the headline to walk her through:** the exogenous predictors (NAO, sunspots) are weak (|r| ≲ 0.16); ENSO's *own* state from **late spring onward** dwarfs them (AMJ +0.62, JAS +0.96). A useful 2026 model should therefore (a) be anchored on **AMJ/JAS persistence**, (b) add **sunspots at a 1-yr lead** as the strongest exogenous term, and (c) treat NAO as a candidate, not a pillar. And nothing skillful is recoverable from the **winter (JFM) side of the spring barrier** — manage that expectation up front.

## 4. Current-state snapshot (context for any forecast talk)

- **ENSO:** weak La Niña has relaxed — ONI −0.4 (DJF 2026) → −0.1 (JFM) → +0.1 (FMA), i.e. **trending toward neutral**.
- **NAO:** strongly positive spring — Mar 2026 **+2.42**, Apr **+1.37** (after a negative Nov–Jan).
- **Sunspots:** **past Solar Cycle 25 max** — 104.8 (2024) ticking down to 97.9 (2025). The declining limb is where the lagged-sunspot signal (§3) would be in play for 2026–27 ENSO.

## 5. Questions to bring

1. ENSO credit confirmed as NOAA CPC ONI (URL in §2) — please add it; are *Weather* and *USDA Crops* datasets still coming (blank credit rows)?
2. Will sunspots & ENSO be refreshed to current, or is 2025 the frozen cutoff?
3. What's her target/output variable — predict ONI itself, or a downstream crop/weather outcome?
4. Given the diagnostics (§3): agreed to anchor on **AMJ/JAS ENSO persistence + 1-yr sunspot lead**, with NAO as a candidate — not an annual-mean NAO+sunspot fit?
5. Do we accept the **spring barrier** (no winter→autumn skill) as a hard constraint on what 2026 forecasts can claim?
