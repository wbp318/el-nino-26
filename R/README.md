# R/ — analysis & modeling

Base-R only — no package installs required. Reads
`../data/processed/panel_monthly.csv` (build it first with the Python pipeline).

| File | Role |
|---|---|
| `correlate.R` | Correlation matrix (full record + 1950+ window) and lead/lag cross-correlations for the three driver pairs. Writes `../results/correlation_*.csv` and `../results/ccf_*.png`; prints peak-lag summary. |
| `model.R` | Predictive scaffold: `target ~ lagged drivers` with a time-ordered train/test split. No-op (with guidance) until the `target` column is populated. |

## Run

```bash
Rscript R/correlate.R
Rscript R/model.R
```

On Windows if `Rscript` isn't on `PATH`:
`"C:\Program Files\R\R-4.5.2\bin\Rscript.exe" R/correlate.R`

## Key functions in `model.R`

- `load_panel()` — read + date-parse the monthly panel.
- `build_design(df, predictors, maxlag)` — add lags `0…maxlag` of each predictor.
- `fit_model(df, target_col, predictors, maxlag, train_frac)` — time-ordered fit,
  returns `list(fit, rmse_test, n_train, n_test)`.

See [`../docs/modeling.md`](../docs/modeling.md) for the full workflow and
[`../docs/methodology.md`](../docs/methodology.md) for interpretation caveats
(seasonality, autocorrelation, the 11-year solar cycle).
