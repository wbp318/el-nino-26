# src/ — Python data pipeline

Fetches and aligns the raw sources into the modeling panels. Requires
`pip install -r ../requirements.txt` (pandas, requests).

| File | Role |
|---|---|
| `fetch_data.py` | Download the 8 raw source files verbatim into `../data/raw/`. Validates each isn't an HTML error page; exits non-zero on any failure. |
| `build_panel.py` | Parse each raw file (`parse_*()`), align onto a common month index, and write `../data/processed/panel_monthly.csv` + `panel_yearly.csv`. Exports `merge_target()` for the modeling step. |
| `verify_forecast.py` | Score a published ENSO forecast (COLA CCSM4 from the May 2026 plume) in `../data/forecasts/` against the observed `enso_nino34_9120` series. See [`../docs/validation.md`](../docs/validation.md). |

## Run

```bash
python src/fetch_data.py     # -> data/raw/
python src/build_panel.py    # -> data/processed/*.csv  (after fetch)
```

## Key functions in `build_panel.py`

- `parse_ssn_monthly() / parse_ssn_yearly()` — SILSO semicolon CSVs (negative SN → NaN).
- `parse_nao_cpc()` — CPC `year month value` ascii.
- `parse_nao_station()` — Hurrell `YEAR Jan…Dec` matrix; `|v|≥99` → missing; ragged last year handled.
- `parse_oni()` — maps the 3-month `SEAS` label to its center month; keeps `ANOM`.
- `parse_nino34_long()` — `YEAR v1…v12` grid; stops at trailing metadata; `-99.99` → NaN.
- `parse_nino34_ersst5()` — CPC ERSSTv5 Niño3.4 anomaly on the **fixed 1991-2020** base (`→ enso_nino34_9120`); Niño3.4 anomaly is the last column (the `ANOM` header repeats).
- `build_monthly()` / `build_yearly()` — concat to the panels; add `clean_1950plus`, `target`.
- `merge_target(panel, target_series)` — align a predictand into the `target` column.

See [`../docs/pipeline.md`](../docs/pipeline.md) and
[`../docs/data-sources.md`](../docs/data-sources.md) for details, and
[`../docs/modeling.md`](../docs/modeling.md) for `merge_target` usage.
