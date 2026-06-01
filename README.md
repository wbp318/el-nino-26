# el-nino-26

A reproducible pipeline that assembles three climate-driver time series —
**North Atlantic Oscillation (NAO)**, **El Niño–Southern Oscillation (ENSO)**, and
**sunspot number** — into aligned monthly and yearly panels, then explores how they
relate and scaffolds a predictive model. The three series are the reusable
**predictors**; the **target** (predictand) is intentionally left open so a weather
outcome or any other series can be dropped in later without re-fetching or
re-structuring anything.

> **Status:** data pipeline + correlation analysis working end-to-end. Modeling is
> scaffolded and waiting on a target variable (see [Target variable](#target-variable)).

---

## Table of contents

- [Why this exists](#why-this-exists)
- [Quick start](#quick-start)
- [Data sources](#data-sources)
- [Time windows: long vs clean](#time-windows-long-vs-clean)
- [The two panels](#the-two-panels)
- [Target variable](#target-variable)
- [Pipeline stages](#pipeline-stages)
- [Analysis & current findings](#analysis--current-findings)
- [Repository layout](#repository-layout)
- [Reproducing from scratch](#reproducing-from-scratch)
- [Licensing & attribution](#licensing--attribution)
- [Further documentation](#further-documentation)

---

## Why this exists

We want to test whether NAO, ENSO, and solar activity (sunspots) carry predictive
signal for some weather outcome. Before any modeling can happen, the three series —
which live in different formats, resolutions, and historical ranges — have to be
fetched from authoritative sources, parsed, and aligned onto a common time axis.
This repo does exactly that, deterministically, so the analysis rests on a clean,
documented, regenerable foundation rather than ad-hoc spreadsheets.

The eventual target is undecided, so the design separates **"get the predictors
right"** (done, stable) from **"model against a target"** (scaffolded, pluggable).

## Quick start

```bash
pip install -r requirements.txt          # pandas, requests

python src/fetch_data.py                 # download 8 raw sources -> data/raw/
python src/build_panel.py                # parse + align -> data/processed/*.csv
Rscript R/correlate.R                    # correlation matrix + lead/lag CCF -> results/
Rscript R/model.R                        # modeling scaffold (no-op until target set)
```

On Windows, if `Rscript` is not on `PATH` it ships at
`C:\Program Files\R\R-4.5.2\bin\Rscript.exe`.

## Data sources

All sources are public, free, and official. Raw files are **not committed** (they are
regenerable and the sunspot data is CC BY-NC) — see [`data/raw/MANIFEST.md`](data/raw/MANIFEST.md)
for exact URLs, retrieval date, and per-file notes, and [`docs/data-sources.md`](docs/data-sources.md)
for a deep dive on each series.

| Series | Variants pulled | Range | Provider |
|---|---|---|---|
| **Sunspots** | daily, monthly mean, yearly mean (V2.0) | 1818 / 1749 / 1700 → | WDC-SILSO, Royal Obs. of Belgium |
| **NAO** | CPC standardized monthly; Hurrell station-based monthly | 1950→ ; 1865→ | NOAA CPC ; NCAR Climate Data Guide |
| **ENSO** | CPC ONI; CPC ERSSTv5 Niño3.4; PSL long Niño3.4 anomaly | 1950→ ; 1950→ ; 1870→ | NOAA CPC ; NOAA PSL |

## Time windows: long vs clean

Two windows are produced so either can be modeled without re-downloading:

- **Long / full record** — extends as far back as each source allows. The common
  monthly overlap of all three concepts is **≈ 1870→present** (ENSO-limited via the
  long Niño3.4; NAO station data starts 1865). Yearly sunspots reach back to **1700**.
- **Clean instrumental window — 1950→present** — fully instrumental, highest
  confidence, all series overlap. Flagged by the `clean_1950plus` column so it is a
  one-line filter.

Pre-1950, NAO is station-based (Lisbon − Iceland sea-level-pressure) and ENSO is
SST-reconstructed: longer reach, but lower confidence. See
[`docs/methodology.md`](docs/methodology.md) for how this affects interpretation.

## The two panels

`src/build_panel.py` writes two aligned tables to `data/processed/`:

**`panel_monthly.csv`** — primary modeling table, one row per month
(1749-01 → present, 3,300+ rows):

| column | meaning |
|---|---|
| `date` | month-start timestamp (index) |
| `nao_cpc` | CPC standardized monthly NAO (1950→) |
| `nao_station` | Hurrell station-based monthly NAO (1865→) |
| `enso_oni` | CPC Oceanic Niño Index anomaly (1950→) |
| `enso_nino34` | PSL long Niño3.4 SST anomaly (1870→) |
| `ssn_monthly` | SILSO monthly mean sunspot number (1749→) |
| `clean_1950plus` | `True` for the fully-instrumental window |
| `target` | empty — the predictand slot |

**`panel_yearly.csv`** — secondary long-baseline table, one row per year
(1700 → present): annual means of the four monthly drivers plus native
`ssn_yearly` (back to 1700), same `clean_1950plus` / `target` columns.

## Target variable

The model predicts whatever lands in the `target` column — undecided by design.
Two ways to populate it:

1. **Python:** `build_panel.merge_target(panel, target_series)` aligns a target
   (indexed by month-start, or by integer year for the yearly panel) into the
   `target` column and returns a new frame. See [`docs/modeling.md`](docs/modeling.md).
2. **By hand:** fill the `target` column of the CSV.

Once populated, `Rscript R/model.R` fits `target ~ lagged drivers` with a
time-ordered train/test split.

## Pipeline stages

```
fetch_data.py      build_panel.py            correlate.R / model.R
 (download)   →     (parse + align)     →      (analyze / model)
 data/raw/          data/processed/*.csv       results/ + console
```

Each stage is independent and re-runnable; intermediate artifacts live on disk so a
later stage never forces an earlier one to re-run. Full description in
[`docs/pipeline.md`](docs/pipeline.md).

## Analysis & current findings

`R/correlate.R` reports a correlation matrix and lead/lag cross-correlations on both
windows. Current sanity-check results (not yet a claim — no target set):

- The two **NAO** measures agree (r ≈ 0.69); the two **ENSO** measures agree
  strongly (r ≈ 0.97) — confirms the parsers and alignment are correct.
- **NAO ↔ ENSO ≈ 0** — consistent with their near-independence.
- **Sunspot ↔ NAO/ENSO** links are weak (peak |r| ≈ 0.06–0.19 across ±24-month
  lags) — consistent with the literature; treat as a sanity gate, not a result.

## Repository layout

```
el-nino-26/
├── README.md              ← this file
├── requirements.txt
├── .gitattributes         ← GitHub Linguist: count every language incl. prose
├── .gitignore             ← raw/processed data + results are regenerable, untracked
├── docs/                  ← deep documentation (see docs/README.md)
├── src/                   ← Python pipeline (fetch_data.py, build_panel.py)
├── R/                     ← stats / modeling (correlate.R, model.R)
├── data/
│   ├── raw/               ← downloaded sources (gitignored) + MANIFEST.md
│   └── processed/         ← panel_monthly.csv, panel_yearly.csv (gitignored)
└── results/              ← correlation CSVs + CCF plots (gitignored)
```

Every subfolder has its own `README.md`.

## Reproducing from scratch

From an empty checkout the four Quick-start commands rebuild everything: raw files,
both panels, and the analysis outputs. Nothing in the analysis depends on data that
isn't regenerable by `fetch_data.py`. The build is deterministic given the upstream
sources (which update monthly as new observations are published).

## Licensing & attribution

- **Sunspot data (SILSO):** CC BY-NC. Credit *WDC-SILSO, Royal Observatory of
  Belgium, Brussels* in any publication.
- NOAA CPC / PSL and NCAR products are US-government / research data; cite the
  provider. Exact citations in [`docs/data-sources.md`](docs/data-sources.md).

## Further documentation

| Doc | Contents |
|---|---|
| [`docs/data-sources.md`](docs/data-sources.md) | Every source: URL, format, range, gotchas, citation |
| [`docs/methodology.md`](docs/methodology.md) | Alignment, resolutions, windows, reconstruction caveats |
| [`docs/pipeline.md`](docs/pipeline.md) | Stage-by-stage walkthrough, how to refresh |
| [`docs/modeling.md`](docs/modeling.md) | Plugging in a target, `fit_model()`, lags, train/test |
| [`docs/glossary.md`](docs/glossary.md) | NAO, ENSO, ONI, Niño3.4, sunspot number V2.0, … |
