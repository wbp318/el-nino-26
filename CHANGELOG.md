# Changelog

All notable changes to **el-nino-26** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Versions remain `0.x` until a predictive **target** is plugged in and a modeling result
is claimed; until then the public surface is the predictor pipeline, the correlation
diagnostics, and the forecast-validation harness.

## [Unreleased]

### Added
- **Continuous integration** (`.github/workflows/ci.yml`) — runs on every push and pull
  request: a `ruff` lint gate (`E9` syntax + `F` pyflakes) and the `pytest` suite across
  a matrix of **Linux + Windows** on **Python 3.10 and 3.12**, with pip caching and
  per-ref concurrency cancellation.
- **Hermetic test suite** (`tests/`) — fixtures every parser and drives the verifier with
  a synthetic panel + forecast CSV, so CI never hits the NOAA / SILSO servers. Covers
  `parse_nino34_ersst5` (last-column selection; April 2026 = +0.23), `parse_oni`
  (season→center-month), `parse_nino34_long` (`-99.99` masking, metadata stop),
  `merge_target` (index-aligned, non-mutating), `observed_seasonal` (centered 3-month
  mean), the verifier's base-period guard, `build_table` per-lead error, and correlation
  suppression. `tests/conftest.py` puts `src/` on the path; `tests/README.md` documents it.
- **`requirements-dev.txt`** — dev/CI dependencies (`pytest`, `ruff`).
- A CI status badge and a *Testing & CI* section in the README; `tests/` and
  `.github/workflows/` added to the repository-layout tree.

## [0.1.0] — 2026-06-02

First tagged release. The predictor pipeline (NAO / ENSO / sunspots) and the
correlation analysis are complete and verified end-to-end; predictive modeling is
scaffolded and waits on a target variable. **The headline addition in this release is a
self-contained forecast-validation harness** that scores a published ENSO forecast —
the **COLA CCSM4** line from the IRI/CPC ENSO prediction plume issued May 2026 — against
observed Niño 3.4 SST anomalies.

### Added

#### Forecast validation — the headline feature
- **`src/verify_forecast.py`** — a standalone scorer. Joins a digitized forecast curve
  to the observed seasonal Niño 3.4 series on the season's center month and reports:
  - **per-lead signed error** (forecast − obs; positive ⇒ the forecast ran warm),
    reported per season rather than aggregated, the honest unit at this sample size;
  - **MAE and RMSE** for the model, the dynamical-model mean, persistence, and
    climatology;
  - **skill framed relative to baselines** — whether COLA beats **persistence** (the
    last season observed at the May-2026 initialization, frozen so it never peeks ahead)
    and **climatology** (zero anomaly);
  - a **sign test** (in how many seasons obs sits above/below the model line);
  - a **base-period guard** that refuses to score if the forecast and observed series
    use different climatology bases;
  - **correlation suppressed below `MIN_N_FOR_CORR = 10`** — a 5-point correlation is
    statistically meaningless and the script says so rather than printing a number.
- **`src/build_panel.py` → `parse_nino34_ersst5()`** — promotes the already-fetched CPC
  ERSSTv5 Niño-region file to a new panel column **`enso_nino34_9120`** (monthly Niño3.4
  anomaly on the **fixed 1991-2020** base). This is the only base-matched truth series
  for the plume; the Niño3.4 anomaly is read by position (the file's `ANOM` header
  repeats four times).
- **`data/forecasts/cola_ccsm4_may2026.csv`** — the COLA CCSM4 gold line (AMJ 2026 →
  JFM 2027), digitized from the plume graphic.
- **`data/forecasts/dynamical_mean_may2026.csv`** — the dynamical-model average line, a
  reference so verification can ask "did observations track COLA *or* the ensemble mean
  better."
- **`docs/validation.md`** — a 12-section reference: what COLA CCSM4 is and its known
  warm/high-amplitude bias; the two halves of a validation; the base-period **and**
  dataset (ERSSTv5 vs OISSTv2) traps; the verifiable-seasons timeline; the metrics; the
  honest small-sample statistical framing; why verification is kept separate from the
  modeling scaffold; a dated runbook; provenance; and limitations.
- **`data/forecasts/README.md`** — schema of the forecast CSVs and the digitization
  provenance.

#### Data pipeline (now versioned)
- **`src/fetch_data.py`** — downloads all 8 raw sources verbatim into `data/raw/`, with
  a guard that rejects HTML error pages and a non-zero exit on any failure.
- **`src/build_panel.py`** — parses each raw file and aligns them onto a common
  month-start index, writing `data/processed/panel_monthly.csv` (1749→) and
  `panel_yearly.csv` (1700→); exports `merge_target()` for the modeling step.
- **Panels** carry a `clean_1950plus` flag (the fully-instrumental window) and an empty
  `target` slot. Monthly columns: `nao_cpc`, `nao_station`, `enso_oni`, `enso_nino34`,
  `enso_nino34_9120`, `ssn_monthly`.

#### Analysis & modeling scaffold
- **`R/correlate.R`** — Pearson correlation matrix (full + 1950+ windows) and lead/lag
  cross-correlations (±24 months) for the conceptual pairs, saved as PNGs.
- **`R/model.R`** — a time-ordered `target ~ lagged drivers` scaffold (`load_panel`,
  `build_design`, `fit_model`) that is a clean no-op until a target is set.

#### Documentation
- `docs/` deep documentation: `data-sources.md`, `methodology.md`, `pipeline.md`,
  `modeling.md`, `validation.md`, `glossary.md`, plus a `README.md` in every subfolder.

### Changed
- Promoted `nino34_cpc_ersst5.ascii` from an archived QC-only file to the live panel
  column `enso_nino34_9120`; updated `README.md`, `docs/data-sources.md`,
  `docs/README.md`, `src/README.md`, and `data/README.md` so none drift.
- `src/verify_forecast.py` console output is **ASCII-only** — the Windows (cp1252)
  console mangles `°`, em dashes, and arrows; units print as `degC`.
- Root `README.md` gains a *Forecast validation* section, a checklist subsection, and a
  table-of-contents entry.

### Notes & caveats (read before trusting a number)
- **Forecast values are digitized** off the plume PNG (≈ ±0.10–0.15 °C read error) —
  IRI's current Quick Look states it is "no longer providing forecast data." Replace the
  `forecast_anom_c` columns wholesale if the numeric table is obtained.
- **Base period vs dataset are two different things.** The truth series matches the
  plume's 1991-2020 base, but the plume's OBS dots are **OISSTv2** while the truth series
  is **ERSSTv5** — the two diverge by up to ~0.5 °C during ENSO events (e.g. April 2026:
  +0.47 °C OISSTv2 vs +0.23 °C ERSSTv5). The script prints this caveat with every result.
- **Not a skill verification.** By ~Oct 2026 only ~4–5 seasons (one ENSO event, one
  model run) are observable, and only the *rise* — the OND peak and decline need the
  Jan–Apr 2027 re-runs.

[0.1.0]: https://github.com/wbp318/el-nino-26/releases/tag/v0.1.0
