# Modeling

The three drivers (NAO, ENSO, sunspots) are **predictors**. The **target**
(predictand) is undecided by design, so this stage is scaffolded and waits for a
target to be set. Until then `R/model.R` is a clean no-op that explains itself.

## Step 1 — set the target

The `target` column starts empty in both panels. Populate it either way:

### Python (recommended)
`src/build_panel.py` exports a helper:

```python
import pandas as pd
import build_panel as bp           # from the src/ directory

panel = bp.build_monthly()         # or pd.read_csv(".../panel_monthly.csv", ...)

# your target, indexed by month-start Timestamps (monthly panel)
target = pd.Series(..., index=pd.DatetimeIndex([...]), name="target")

panel = bp.merge_target(panel, target)   # aligns by index into `target`
panel.to_csv("data/processed/panel_monthly.csv")
```

`merge_target` reindexes the target onto the panel's index (so it tolerates a target
with different coverage) and leaves the predictors untouched. For the yearly panel,
index the target by **integer year** instead.

### By hand
Fill the `target` column directly in `data/processed/panel_monthly.csv`.

> When Amelia's numbers arrive: drop them into a `Series`/CSV keyed by date and run
> `merge_target`. No re-fetch, no re-structure.

## Step 2 — fit

```bash
Rscript R/model.R
```

`R/model.R` provides:

- **`load_panel()`** — reads `panel_monthly.csv`, parses dates.
- **`build_design(df, predictors, maxlag = 6)`** — adds lags `0…maxlag` of each
  predictor (the drivers *lead* the target), as columns `"<pred>_l<k>"`.
- **`fit_model(df, target_col = "target", predictors = c("nao_cpc","enso_oni","ssn_monthly"), maxlag = 6, train_frac = 0.8)`**
  — complete-cases the design, fits `lm(target ~ all lagged predictors)` on the first
  `train_frac` of rows (time-ordered, no shuffling — this is a time series), predicts
  the held-out tail, and returns `list(fit, rmse_test, n_train, n_test)`.

`main()` runs `fit_model(load_panel())` and prints test RMSE + `summary(fit)` once a
target exists; otherwise it prints guidance and exits 0.

## Design choices baked in

- **Lagged predictors, not contemporaneous only.** Climate drivers lead surface
  outcomes; lags 0–6 months are the default, widen via `maxlag`.
- **Time-ordered split.** Train on the past, test on the future — never random
  k-fold on a time series (it leaks).
- **Drivers lead the target.** Lags shift predictors *backward* so row *t* uses
  driver values from *t, t−1, …, t−k*.

## Suggested next steps (when a target is set)

1. Pick the **window** (`clean_1950plus` for a high-confidence baseline; full record
   for length) — filter before fitting.
2. Pick **which NAO/ENSO variant** to use as the predictor (CPC vs station/long).
   Both are in the panel; it's a column choice, not a re-fetch.
3. Address **seasonality and autocorrelation** (see
   [`methodology.md`](methodology.md)) — consider seasonal subsets/anomalies and
   block resampling for honest significance.
4. Compare the linear baseline against a regularized fit (lags are collinear) and a
   simple persistence/climatology benchmark before claiming skill.
