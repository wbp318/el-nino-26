# data/forecasts/

Hand-authored **forecast** series to be scored against observations by
[`src/verify_forecast.py`](../../src/verify_forecast.py). Unlike `data/raw/` and
`data/processed/` (regenerable, gitignored), these files are **committed** — they are
digitized from a published forecast graphic and cannot be re-downloaded.

See [`docs/validation.md`](../../docs/validation.md) for the full validation design and
the scientific caveats.

## Files

| File | What it is |
|---|---|
| `cola_ccsm4_may2026.csv` | The **COLA CCSM4** line (gold) from the IRI/CPC ENSO prediction plume issued **May 2026** — the steepest/most aggressive member, peaking ~+2.95 °C in OND 2026. |
| `dynamical_mean_may2026.csv` | The **dynamical-model average** line from the same plume (peak ~+2.2 °C) — a reference so verification can ask "did observations track COLA *or* the ensemble mean better." |

## Schema

| Column | Meaning |
|---|---|
| `target_season` | 3-month season label (`AMJ`, `MJJ`, … `JFM`), same labels as the ONI. |
| `center_month_date` | Month-start `Timestamp` of the season's **center month** (`AMJ`→May, … `OND`→Nov, `DJF`→Jan-of-next-year). Matches `build_panel.parse_oni`'s convention so it joins directly to the observed seasonal series. |
| `forecast_anom_c` | Predicted Niño 3.4 SST anomaly (°C). |
| `base_period` | Climatology base of the anomaly. **Must be `1991-2020`** to match the observed truth series (`enso_nino34_9120`); `verify_forecast.py` refuses to score a mismatch. |
| `lead_months` | Months from the **May 2026** forecast initialization to the season's center month (May→0, Jun→1, …). Low leads sit in the spring predictability barrier. |

## Provenance — these numbers are DIGITIZED, not downloaded

> ⚠️ **Every `forecast_anom_c` value was eyeballed off the May 2026 plume PNG**
> (read error ≈ ±0.10–0.15 °C). IRI's current Quick Look page states it is "no longer
> providing forecast data" and directs users to a collaboration request form, so the
> per-model numeric tables are not publicly downloadable for this issuance. The
> early-lead values (AMJ/MJJ) are the least certain because the plume lines bunch near
> the April-OBS anchor.
>
> If you obtain the exact numeric forecast (via IRI's collaboration form), replace the
> `forecast_anom_c` column wholesale and note it here.

- **Source graphic:** IRI/CPC "Model Predictions of ENSO from May 2026" (Niño 3.4 SST Anomaly).
- **Model label check:** confirm the gold line is labeled **COLA CCSM4** on the IRI
  image — the *CPC NMME* plume labels the same family `NCAR_CCSM4` / `NCAR_CESM1`.
- **Digitized:** June 2026.
