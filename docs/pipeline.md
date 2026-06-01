# Pipeline

Three independent, re-runnable stages. Each writes its output to disk so a later
stage never forces an earlier one to re-run.

```
src/fetch_data.py      src/build_panel.py          R/correlate.R · R/model.R
   download         →     parse + align        →      analyze · model
 → data/raw/             → data/processed/*.csv       → results/ · console
```

## Stage 1 — `src/fetch_data.py`  (download)

Downloads the 8 raw source files into `data/raw/`, saving each verbatim. A `SOURCES`
dict maps `label → (url, filename, note)`; add a source by adding one entry.

- **Guard:** the SILSO and some NOAA endpoints occasionally serve an HTML
  error/wrapper page instead of data — `fetch()` rejects any body that starts with
  `<!doctype html` / `<html>`, so a bad fetch fails loudly instead of poisoning the
  parse step.
- **Idempotent:** re-running simply re-downloads (sources update monthly).
- **Exit code:** non-zero if any source fails, naming the failures.

Run: `python src/fetch_data.py`

## Stage 2 — `src/build_panel.py`  (parse + align)

One `parse_*()` per source returns a tidy `Series`; `build_monthly()` /
`build_yearly()` concatenate them onto a common index. See
[`methodology.md`](methodology.md) for the alignment rules and
[`data-sources.md`](data-sources.md) for each file's format.

Outputs:
- `data/processed/panel_monthly.csv` — primary, one row per month (1749→).
- `data/processed/panel_yearly.csv` — secondary, one row per year (1700→).

Both carry `clean_1950plus` and an empty `target`. The module also exports
`merge_target(panel, target_series)` for the modeling step (see
[`modeling.md`](modeling.md)).

On run it prints a summary — shape, date span, and per-column non-null counts with
the first valid date — which doubles as a quick integrity check.

Run: `python src/build_panel.py`  (after stage 1)

## Stage 3 — `R/correlate.R` and `R/model.R`  (analyze / model)

Base-R only (no package installs needed).

- **`correlate.R`** — correlation matrix (full + 1950+) → `results/correlation_*.csv`;
  lead/lag CCF plots → `results/ccf_*.png`; peak-lag summary to console.
- **`model.R`** — modeling scaffold. No-op with a clear message while `target` is
  empty; once set, fits `target ~ lagged drivers` with a time-ordered train/test
  split and prints test RMSE + summary.

Run: `Rscript R/correlate.R` then `Rscript R/model.R`
(Windows path: `C:\Program Files\R\R-4.5.2\bin\Rscript.exe`.)

## Refreshing the data

The upstream series update monthly. To pull the latest, just re-run stages 1→2→3.
Nothing is cached beyond the files on disk, and the build is deterministic given the
current upstream data.

## Extending with a new source

1. Add an entry to `SOURCES` in `fetch_data.py`.
2. Write a `parse_<name>()` in `build_panel.py` returning a month-indexed `Series`,
   and add it to the `concat` list in `build_monthly()`.
3. Document it in `data-sources.md` and `data/raw/MANIFEST.md`.
4. If it should be a model predictor, add it to the `predictors` default in
   `model.R` / `fit_model()`.

## What is and isn't committed

`data/raw/`, `data/processed/`, and `results/` are **gitignored** — all regenerable,
some large, and the sunspot data is CC BY-NC. What's tracked: the scripts, the docs,
`data/raw/MANIFEST.md`, and `.gitkeep` placeholders. A fresh clone rebuilds
everything by running the three stages.
