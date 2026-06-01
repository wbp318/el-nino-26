# data/processed/

Aligned modeling panels written by `src/build_panel.py`. **Gitignored** — regenerate
with `python src/build_panel.py` (after `python src/fetch_data.py`).

## `panel_monthly.csv` — primary, one row per month (1749-01 → present)

| column | type | meaning | coverage |
|---|---|---|---|
| `date` | date | month-start timestamp (index) | 1749-01 → |
| `nao_cpc` | float | CPC standardized monthly NAO | 1950→ |
| `nao_station` | float | Hurrell station-based monthly NAO | 1865→ |
| `enso_oni` | float | CPC Oceanic Niño Index anomaly | 1950→ |
| `enso_nino34` | float | PSL long Niño3.4 SST anomaly | 1870→ |
| `ssn_monthly` | float | SILSO monthly mean sunspot number | 1749→ |
| `clean_1950plus` | bool | `True` for the fully-instrumental window | — |
| `target` | (empty) | predictand slot — fill via `merge_target()` | — |

Missing values are explicit (blank/`NaN`) — no interpolation. Each column begins at
its source's first valid date; earlier rows are `NaN` for that column.

## `panel_yearly.csv` — secondary, one row per year (1700 → present)

Annual means of `nao_cpc`, `nao_station`, `enso_oni`, `enso_nino34`, plus native
`ssn_yearly` (back to 1700), with the same `clean_1950plus` and `target` columns.
Use for cycle-scale / long-baseline analysis.

See [`../../docs/methodology.md`](../../docs/methodology.md) for alignment rules and
the long-vs-1950 windows.
