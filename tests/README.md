# tests/

Hermetic unit tests for the Python pipeline, run by CI on every push and pull request
(see [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

**No network.** Every test fixtures its inputs — tiny in-memory sample files for the
parsers, and a synthetic panel + forecast CSV for the verifier — so the suite never hits
the NOAA / SILSO servers and is fully deterministic. Integration against the live
sources is intentionally *not* part of CI (those endpoints are flaky and update monthly);
verify the real fetch locally with `python src/fetch_data.py`.

## Run

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q                     # from the repo root
ruff check --select E9,F src tests   # the same lint gate CI runs
```

`conftest.py` puts `src/` on `sys.path` so the scripts import as top-level modules.

## What's covered

| File | Covers |
|---|---|
| `test_build_panel.py` | `parse_nino34_ersst5()` selects the Niño3.4 anomaly by position (the `ANOM` header repeats; April 2026 = +0.23); `parse_oni()` season→center-month mapping (DJF→Jan, NDJ→Dec); `parse_nino34_long()` masks `-99.99` and ignores trailing metadata; `merge_target()` aligns by index without mutating the input. |
| `test_verify_forecast.py` | `observed_seasonal()` is a centered 3-month mean and requires `enso_nino34_9120`; the **base-period guard** rejects a mismatch and accepts a match; `build_table()` computes per-lead signed error, the `verifiable` flag, a zero climatology and a frozen persistence baseline; `summarize()` runs and suppresses correlation below `MIN_N_FOR_CORR`. |

## Conventions

- Pure functions are tested directly; module-level paths (`build_panel.RAW`,
  `verify_forecast.PANEL` / `FORECAST_DIR` / `FORECASTS`) are redirected with
  `monkeypatch` to `tmp_path`, so nothing touches the real `data/` tree.
- Numeric assertions use `pytest.approx`.
