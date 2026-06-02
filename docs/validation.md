# Forecast validation — the COLA CCSM4 ENSO model

How `el-nino-26` validates a published ENSO **forecast** against observations, and the
worked case it was built for: scoring the **COLA CCSM4** line from the IRI/CPC ENSO
prediction plume issued **May 2026** against observed Niño 3.4 SST anomalies, starting
~4 months after issuance.

This is a different operation from the [modeling](modeling.md) scaffold. Modeling fits
`target ~ lagged drivers` to *discover* a relationship; validation *differences an
externally-produced forecast curve against truth* and compares it to baselines. They
deliberately do not share code — see [§9](#9-why-not-reuse-merge_target--modelr).

---

## Table of contents

1. [What we are validating](#1-what-we-are-validating)
2. [What COLA CCSM4 is](#2-what-cola-ccsm4-is)
3. [The two halves of a validation](#3-the-two-halves-of-a-validation)
4. [The base-period & dataset trap](#4-the-base-period--dataset-trap)
5. [What is verifiable in 4 months](#5-what-is-verifiable-in-4-months)
6. [Verification metrics](#6-verification-metrics)
7. [The honest statistical framing](#7-the-honest-statistical-framing)
8. [Files & code](#8-files--code)
9. [Why not reuse merge_target / model.R](#9-why-not-reuse-merge_target--modelr)
10. [The 4-month runbook](#10-the-4-month-runbook)
11. [Provenance & sources](#11-provenance--sources)
12. [Limitations & future work](#12-limitations--future-work)

---

## 1. What we are validating

The IRI/CPC ENSO prediction plume ("Model Predictions of ENSO from May 2026") shows
~20+ models forecasting the Niño 3.4 SST anomaly as a set of overlapping 3-month
seasonal means (FMA, AMJ, MJJ, … JFM). **COLA CCSM4** is the gold line — the single
**most aggressive** member, ramping steeply to a peak of **≈ +2.95 °C around OND 2026**
(Oct-Nov-Dec, centered November) before declining to ≈ +2.45 °C by JFM 2027. The
dynamical-model average peaks far lower, around **+2.2 °C**.

The validation question: **as observations come in, does the observed Niño 3.4 anomaly
track the COLA CCSM4 line — and does it track COLA better or worse than the ensemble
mean, a persistence forecast, and climatology?**

## 2. What COLA CCSM4 is

- **COLA-RSMAS-CCSM4** — a fully-coupled ocean–atmosphere–land dynamical seasonal
  forecast model built on NCAR's Community Climate System Model v4 (CCSM4), run as a
  collaboration of the **Center for Ocean-Land-Atmosphere Studies** (COLA, now at George
  Mason University), the University of Miami's **RSMAS**, and **NCAR**.
- It is one **dynamical member** of the North American Multi-Model Ensemble (NMME),
  whose member forecasts feed the IRI/CPC plume. It is one estimate, not "the forecast."
- **Known warm / high-amplitude bias.** CCSM4 overestimates ENSO amplitude — Gent et al.
  (2011) note its ENSO variability has a more realistic *frequency* than CCSM3
  "although the amplitude is too large compared to observations." This is consistent
  with COLA CCSM4 being the highest line on the May 2026 plume. **Practical
  consequence:** if El Niño verifies strong, COLA can look "right" partly because its
  bias happened to coincide with a big event — right for the wrong reason — and it would
  be badly wrong for a weak/moderate event. The [sign test](#6-verification-metrics) and
  the ensemble-mean comparison guard against reading bias-coincidence as skill.
- **Label check.** The *CPC NMME* plume now labels this family `NCAR_CCSM4` /
  `NCAR_CESM1`; "COLA CCSM4" is the IRI plume's naming. Confirm the gold line's label on
  the actual May 2026 IRI image.

## 3. The two halves of a validation

A validation needs two series aligned on the **same dates**, the **same 3-month
seasonal averaging**, and the **same climatology base period**.

### The FORECAST side — new to this repo

The plume's gold line is nine seasonal anomalies on a 1991-2020 base. Nothing in the
original pipeline stores forecast values (it ingests *observed/reconstructed driver*
series plus one empty `target` slot). A forecast curve is neither a driver nor the
predictand, so it gets its own committed file:
[`data/forecasts/cola_ccsm4_may2026.csv`](../data/forecasts/cola_ccsm4_may2026.csv)
(plus `dynamical_mean_may2026.csv` as the ensemble-mean reference). **Those values are
digitized off the published PNG** — IRI no longer posts numeric forecast tables. See
[§11](#11-provenance--sources).

### The TRUTH side — the pipeline already ingests it

The observed Niño 3.4 anomaly already flows through `build_panel.py` in three forms.
Only one is a clean base-period match to the plume (see [§4](#4-the-base-period--dataset-trap)):

| Panel column | Source file | Base period | Seasonal? | Matches plume (1991-2020)? |
|---|---|---|---|---|
| `enso_oni` | `oni_cpc.ascii.txt` | sliding 30-yr | yes (already centered 3-mo mean) | **No** — sliding base |
| `enso_nino34` | `nino34_long_anom.data` | 1981-2010 | no (monthly) | **No** — cooler base, warm offset |
| **`enso_nino34_9120`** | `nino34_cpc_ersst5.ascii` | **1991-2020** | no (monthly) | **Yes** — exact base match |

`enso_nino34_9120` is produced by `parse_nino34_ersst5()`, added in this work. The
source file was already being **fetched and archived** (it had been a QC cross-check);
this validation simply promotes it to a panel column.

## 4. The base-period & dataset trap

This is the single most consequential, most silent source of error. Two distinct axes:

### 4a. Climatology base period

Anomalies are defined relative to a base-period average. The plume uses a **fixed
1991-2020** climatology. Because Niño 3.4 has warmed since the mid-20th century:

- A **1981-2010** base (the `enso_nino34` column) reads **systematically cooler** than
  1991-2020 by roughly **+0.1 to +0.2 °C** (≈ +0.25 °C worst case). Score the plume
  against it and that offset masquerades as "COLA ran too warm."
- The **ONI's sliding** base (`enso_oni`) deliberately removes the warming trend the
  plume keeps in. Differencing a fixed-base forecast against a sliding-base observation
  re-introduces exactly that trend as spurious model bias. (The ONI base was also
  scheduled to advance at the start of 2026 — another moving part to avoid.)

➡️ **Use `enso_nino34_9120` (fixed 1991-2020).** `verify_forecast.py` enforces this with
a guard that **refuses to score** if the forecast CSV's `base_period` ≠ the observed
series' base.

### 4b. SST dataset — base period alone is not enough

Even on a matched base, the *dataset* differs:

- The plume's **OBS dots are OISSTv2** (IRI's real-time/initialization product), **not
  ERSSTv5**. The two can diverge by **up to ~0.5 °C during ENSO events**.
- Concrete, current example: **April 2026 reads +0.47 °C in IRI's OISSTv2 text but
  +0.23 °C in the CPC ERSSTv5 91-20 file** — a 0.24 °C gap in one month, same base era.
  (The +0.23 °C value is verified directly in this repo's
  `data/raw/nino34_cpc_ersst5.ascii`; the +0.47 °C OISSTv2 figure is from IRI.)

➡️ **Decision for this repo:** use **ERSSTv5/1991-2020** (`enso_nino34_9120`) as the
default truth — it is the official-monitoring view and fits the CPC-heavy stack — and
**print the OISSTv2 caveat with every result** so the ~0.2–0.5 °C dataset gap is never
forgotten. A future option is to add an OISSTv2/1991-2020 source to match the plume's
dots exactly ([§12](#12-limitations--future-work)). **Never** silently substitute
`nino34_long_anom` (1981-2010) or `enso_oni` (sliding).

## 5. What is verifiable in 4 months

Observed Niño 3.4 lags the calendar, and a *centered* 3-month season needs the month
*after* its center. CPC also revises recent values for ~2 months.

- The monthly ERSSTv5 file lags ~1 month (e.g. in early July the latest month is May).
- A centered season therefore trails monthly availability by one more step.
- CPC's seasonal ONI updates by the 5th of each month and is revisable for ~2 months.

**Verifiable by end of October 2026** (with the latest 1–2 flagged provisional):

| Season | Center month | Status by Oct 2026 |
|---|---|---|
| AMJ 2026 | May | final |
| MJJ 2026 | Jun | final / near-final |
| JJA 2026 | Jul | final / near-final |
| JAS 2026 | Aug | provisional, settling |
| ASO 2026 | Sep | borderline — needs the Oct monthly value (~mid-Nov) |

**NOT verifiable until 2027:**

| Season | Center | First estimate | Note |
|---|---|---|---|
| **OND 2026** | Nov | ~early **Jan 2027** | the COLA **peak** (~+2.95 °C) |
| NDJ 2026 | Dec | ~early Feb 2027 | decline |
| DJF 2026-27 | Jan | ~early Mar 2027 | decline |
| JFM 2027 | Feb | ~early Apr 2027 | decline (~+2.45 °C) |

### The key insight: the ramp is what's testable, and it's the most diagnostic part

You cannot touch the headline +2.95 °C peak in 4 months — but COLA CCSM4 is the
**steepest line on the chart**, and its steepness lives in exactly the AMJ→ASO window
you *can* observe. CCSM4's documented warm-amplitude bias, if it is going to show up,
shows up as the **rise running hotter than observations**. So if `err_cola` is already
strongly positive by JJA/JAS, that is the early tell — caught in October instead of
waiting for January 2027.

## 6. Verification metrics

`verify_forecast.py` computes, over the verifiable seasons:

- **Per-lead signed error** = forecast − obs (positive ⇒ forecast ran warm). Reported
  per season, *not* aggregated — the honest unit at this sample size.
- **MAE and RMSE** for COLA, the dynamical mean, persistence, and climatology.
- **Skill framing relative to baselines.** "Close to obs" alone is meaningless; the
  script reports whether COLA **beats persistence and climatology** by RMSE — the only
  defensible sense of "skill."
  - **Persistence** = the last season observed *at the May 2026 initialization*, carried
    forward to every lead (frozen at init, so it never peeks at later observations).
  - **Climatology** = zero anomaly on the 1991-2020 base.
- **Sign test** = in how many seasons obs sits above/below the COLA line (and, via the
  reference file, relative to the ensemble mean). The soundest small-sample statement
  about a one-sidedly hot model.
- **Correlation is suppressed** below `MIN_N_FOR_CORR = 10` — see [§7](#7-the-honest-statistical-framing).

Output table: [`data/processed/verify_cola_ccsm4.csv`](../data/processed/) (gitignored,
regenerable) plus the console summary.

## 7. The honest statistical framing

> **n ≈ 4–5 seasons, from one ENSO event, one model run. This is NOT a skill
> verification.**

- A single forecast landing close is not skill; only many forecasts scored against
  observations reveal whether predictions are reliable (IRI, *The Truth About
  Verification*).
- A correlation over ~5 points is meaningless — its confidence interval spans roughly
  −0.8 to +0.95. The script refuses to print one until n ≥ 10–12.
- The **spring predictability barrier**: a May-initialized forecast has intrinsically
  lower skill at short leads regardless of model quality. Do not over-read an early
  AMJ/MJJ miss as evidence about COLA specifically.
- COLA is the **most aggressive single member**; comparing observations only to it is
  misleading. Always also report whether obs is above/below the **ensemble mean** —
  the literature consensus is that the multi-model mean matches the best single model
  and beats the *average* single model, and you cannot pick the best model in advance.

Defensible conclusions: per-lead signed error, RMSE-vs-baselines, and the sign test.
Indefensible: a correlation, or any "validated / busted" verdict, from this sample.

## 8. Files & code

| Path | Role | Tracked? |
|---|---|---|
| `data/forecasts/cola_ccsm4_may2026.csv` | digitized COLA CCSM4 forecast line | **committed** |
| `data/forecasts/dynamical_mean_may2026.csv` | digitized dynamical-mean reference | **committed** |
| `data/forecasts/README.md` | schema + digitization provenance | committed |
| `src/build_panel.py` → `parse_nino34_ersst5()` | promotes ERSSTv5/91-20 to `enso_nino34_9120` | committed |
| `src/verify_forecast.py` | the scorer | committed |
| `data/processed/panel_monthly.csv` | gains the `enso_nino34_9120` column | gitignored (regenerable) |
| `data/processed/verify_cola_ccsm4.csv` | scoring output | gitignored (regenerable) |

`src/fetch_data.py` is unchanged — it already fetches `nino34_cpc_ersst5.ascii`.

### Running it

```bash
python src/fetch_data.py        # already pulls the ERSSTv5 91-20 file
python src/build_panel.py       # now also builds enso_nino34_9120
python src/verify_forecast.py   # scores the forecast; writes verify_cola_ccsm4.csv
```

`verify_forecast.py` reads `panel_monthly.csv`, takes a **centered 3-month running
mean** of `enso_nino34_9120` (matching the plume's seasonal convention), joins it to
the forecast CSV on `center_month_date`, and prints the metrics in [§6](#6-verification-metrics).
Before the rise is observed it cleanly reports "Nothing observed yet."

## 9. Why not reuse `merge_target` / `model.R`

You *could* `merge_target(panel, observed_seasonal())` and lean on `R/model.R`. **Don't,
for verification.** `model.R` fits `target ~ lagged drivers` with a time-ordered
train/test split — a **predictor→predictand regression** scaffold for discovering
relationships in the driver series (and the home for Amelia's eventual target).
Verification is a different operation: nothing is *fitted*; an external curve is
*differenced* against truth and compared to fixed baselines. Shoehorning it in would
(a) misuse the reserved `target` column, (b) drag in lag construction and a train/test
split that are nonsense for ~5 deterministic forecast points, and (c) force
`correlate.R` to special-case a forecast column. A standalone `verify_forecast.py` keeps
the modeling scaffold pure. **`merge_target` stays reserved for its real job.**

## 10. The 4-month runbook

> R isn't on `PATH`; invoke `"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"` explicitly.
> (R is not needed for verification — `verify_forecast.py` is pure Python.)

### Now (June 2026) — set up while the plume is fresh
1. Digitize the gold line into `data/forecasts/cola_ccsm4_may2026.csv` (done — values
   are estimates, see [§11](#11-provenance--sources)). Confirm the label is "COLA
   CCSM4" on the actual IRI image.
2. (Recommended) Digitize the dynamical-mean line into `dynamical_mean_may2026.csv`
   (done) so October can answer "did obs track COLA or the ensemble mean better."
3. `python src/build_panel.py` → confirm `enso_nino34_9120` spans 1950-01 → 2026-04 and
   reads **+0.23** for April 2026 (sanity fixture against the raw file).
4. `python src/verify_forecast.py` → dry run. Expect "Nothing observed yet" (the rise
   hasn't been observed), exercising the base-period guard and the correlation gate.
5. Commit the forecast CSVs + parser + verify script + this doc.

### Monthly (early Jul / Aug / Sep / Oct, just after the 5th)
6. `python src/fetch_data.py && python src/build_panel.py` — re-pull and rebuild.
7. `python src/verify_forecast.py` — running preview. Watch the **ramp**: a growing
   positive `err_cola` by JJA/JAS is the warm-amplitude bias surfacing early.

### ~Oct 2026 (run shortly after the Oct 5 update) — the real check
8. Final fetch + rebuild + verify. Expect AMJ–JAS scored; ASO provisional.
9. Read the **per-lead signed error**, not an aggregate.
10. Judge **vs persistence and climatology** (the script prints BEATS / loses to), not
    absolute closeness.
11. Apply the [§7](#7-the-honest-statistical-framing) caveats verbatim in any writeup
    (n=1 event, spring barrier, peak untouched, ERSSTv5 ≠ OISSTv2, right-for-wrong-reasons).

### Jan 2027 / Apr 2027 — the peak & decline
12. Re-run after early Jan 2027 (first OND-2026 estimate) and early Apr 2027 (JFM-2027)
    to finally score the peak and decline.

## 11. Provenance & sources

**Digitized (eyeballed off the May 2026 plume PNG, ≈ ±0.10–0.15 °C):** every
`forecast_anom_c` in both forecast CSVs — COLA peak ~2.95 (OND) and the steep
JAS/ASO/SON rise are the load-bearing numbers; AMJ/MJJ are least certain (lines bunch
near the April-OBS anchor). IRI's current Quick Look states it is "no longer providing
forecast data," so the per-model numeric tables are not downloadable for this issuance;
the 2012-era public tables prove they once were. To get exact numbers, use IRI's
collaboration request form, then replace the `forecast_anom_c` columns wholesale.

**Verified in this repo:** April 2026 Niño 3.4 = **+0.23 °C** in
`data/raw/nino34_cpc_ersst5.ascii` (ERSSTv5, 1991-2020), used as the parser sanity
fixture.

**Sourced (IRI / CPC / literature, via web research, June 2026):**
- IRI plume uses 1991-2020 base; OBS anchored to OISSTv2 — <https://iri.columbia.edu/our-expertise/climate/forecasts/enso/current/>
- ONI definition & sliding base — <https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php>
- ERSSTv5 91-20 monthly file — <https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii>
- CCSM4 ENSO amplitude bias (Gent et al. 2011) — <https://journals.ametsoc.org/view/journals/clim/24/19/2011jcli4083.1.xml>
- NMME / COLA-RSMAS-CCSM4 — <https://journals.ametsoc.org/view/journals/bams/103/3/BAMS-D-20-0327.1.xml>
- Verification philosophy — <https://iri.columbia.edu/news/the-truth-about-verification/>
- Spring predictability barrier — <https://www.climate.gov/news-features/blogs/enso/spring-predictability-barrier-we%E2%80%99d-rather-be-spring-break>

## 12. Limitations & future work

- **Digitized forecast values** carry ±0.10–0.15 °C read error. Replace with the
  numeric IRI table if obtained.
- **Dataset mismatch (ERSSTv5 vs OISSTv2)** persists even with the base matched —
  ~0.2–0.5 °C in events. A future improvement is to add an **OISSTv2/1991-2020** source
  to `fetch_data.py` and verify against the product the plume's dots are actually drawn
  from. The current default is documented and flagged, not hidden.
- **RONI.** CPC moved its primary ENSO-monitoring index to the Relative Oceanic Niño
  Index in Feb 2026. The plume targets raw Niño 3.4 (ONI-style) anomaly, so this repo
  keeps validating against raw Niño 3.4 — but NOAA's headline ENSO *status* is now
  RONI-based and can diverge in a warming-adjusted way.
- **Sample size.** The decisive peak/decline check requires the Jan–Apr 2027 re-runs;
  the October check is the ramp only.
- **Damped persistence** (a decay toward climatology) is a stronger baseline than plain
  persistence and could be added if the sample grows.

---

*See also: [`methodology.md`](methodology.md) (alignment, seasonality, autocorrelation),
[`data-sources.md`](data-sources.md) (the ERSSTv5 source file), [`modeling.md`](modeling.md)
(the separate predictor→target scaffold), [`glossary.md`](glossary.md).*
