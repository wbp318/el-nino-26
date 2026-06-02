"""Score the May-2026 IRI/CPC plume forecasts against observed Niño 3.4.

Compares the COLA CCSM4 forecast (and, if present, the dynamical-model mean) from
data/forecasts/ against observed ERSSTv5 Niño 3.4 3-month-mean anomalies on the
matching 1991-2020 base period, plus persistence and climatology baselines.

Run:  python src/verify_forecast.py   (after build_panel.py)
Outputs: data/processed/verify_cola_ccsm4.csv  +  a console summary.

THIS IS DESCRIPTIVE PER-LEAD ERROR, NOT A SKILL VERIFICATION. By ~Oct 2026 only
~4-5 seasons (one ENSO event, one model run) are observable, so no correlation is
reported below MIN_N_FOR_CORR. Truth is ERSSTv5/1991-2020; the plume's OBS dots are
OISSTv2 (up to ~0.5 °C apart during ENSO events) — same base period is NOT the same
dataset, and that caveat is printed with every result. See docs/validation.md.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FORECAST_DIR = ROOT / "data" / "forecasts"
PANEL = ROOT / "data" / "processed" / "panel_monthly.csv"
OUT = ROOT / "data" / "processed" / "verify_cola_ccsm4.csv"

OBS_COL = "enso_nino34_9120"     # ERSSTv5, fixed 1991-2020 base (parse_nino34_ersst5)
OBS_BASE = "1991-2020"
INIT_DATE = pd.Timestamp(2026, 5, 1)   # forecast initialization (May 2026 issuance)
MIN_N_FOR_CORR = 10              # below this a correlation is statistically meaningless

# label -> filename. "cola" is the primary forecast; the rest are reference lines.
FORECASTS = {
    "cola": "cola_ccsm4_may2026.csv",
    "dynmean": "dynamical_mean_may2026.csv",
}


def observed_seasonal() -> pd.Series:
    """Centered 3-month running mean of the 1991-2020 monthly Niño 3.4 anomaly,
    keyed by center month — the same seasonal convention as the plume x-axis and
    the ONI (value at month t = mean of t-1, t, t+1)."""
    panel = pd.read_csv(PANEL, parse_dates=["date"]).set_index("date")
    if OBS_COL not in panel.columns:
        raise SystemExit(f"{OBS_COL} missing from {PANEL.name} — rebuild the panel "
                         "with build_panel.parse_nino34_ersst5() wired in.")
    return (panel[OBS_COL]
            .rolling(window=3, center=True, min_periods=3).mean()
            .rename("obs_anom_c"))


def load_forecast(fname: str) -> pd.DataFrame:
    """Load a forecast CSV, asserting its base period matches the observed series."""
    fc = pd.read_csv(FORECAST_DIR / fname, parse_dates=["center_month_date"])
    bases = set(fc["base_period"].astype(str).unique())
    if bases != {OBS_BASE}:          # base-period guard — refuse to score a mismatch
        raise SystemExit(f"BASE MISMATCH in {fname}: {sorted(bases)} vs observed "
                         f"{OBS_BASE}. Re-base before differencing; refusing to score.")
    return fc.set_index("center_month_date")


def build_table():
    """Join forecasts + observations + baselines into one scoring table.

    Returns (table, loaded_labels, last_obs_date)."""
    loaded = {k: load_forecast(v) for k, v in FORECASTS.items()
              if (FORECAST_DIR / v).exists()}
    if "cola" not in loaded:
        raise SystemExit(f"Primary forecast {FORECASTS['cola']} not found in {FORECAST_DIR}.")
    cola = loaded["cola"]
    obs = observed_seasonal()

    t = cola[["target_season", "forecast_anom_c", "lead_months"]].copy()
    t = t.rename(columns={"forecast_anom_c": "cola_anom_c"})
    t = t.join(obs)                  # obs is NaN for seasons not yet observed

    # reference forecast line(s), e.g. the dynamical-model mean
    refs = [k for k in loaded if k != "cola"]
    for label in refs:
        t[f"{label}_anom_c"] = loaded[label]["forecast_anom_c"]

    # baselines — same base period and seasonal averaging as forecast & obs.
    # climatology = zero anomaly. persistence = the last season observed AT
    # INITIALIZATION carried forward (frozen at init, so it is a fair forecast and
    # never peeks at observations that postdate the May 2026 issuance).
    t["clim_anom_c"] = 0.0
    init_obs = obs[obs.index <= INIT_DATE].dropna()
    if init_obs.empty:
        raise SystemExit("No observed season at/before the init date — cannot form "
                         "a persistence baseline.")
    t["persist_anom_c"] = init_obs.iloc[-1]

    # signed errors (source minus obs); positive => the source ran warm
    sources = ["cola", "persist", "clim"] + refs
    for label in sources:
        t[f"{label}_err"] = t[f"{label}_anom_c"] - t["obs_anom_c"]

    last_obs_date = obs.dropna().index.max()
    t["verifiable"] = t["obs_anom_c"].notna()
    # provisional: CPC revises values for ~2 months, so flag the latest ~2 seasons
    t["provisional"] = t.index >= (last_obs_date - pd.DateOffset(months=1))
    return t, loaded, last_obs_date


def _rmse(e: pd.Series) -> float:
    return float((e.dropna() ** 2).mean() ** 0.5)


def summarize(t: pd.DataFrame, loaded: dict, last_obs_date) -> None:
    refs = [k for k in loaded if k != "cola"]
    scored = t[t["verifiable"]]
    n = len(scored)

    print(f"Observed truth : {OBS_COL} (ERSSTv5, {OBS_BASE} base).")
    print("Dataset caveat : the plume's OBS dots are OISSTv2 - up to ~0.5 degC apart "
          "from ERSSTv5 during ENSO events. Same base period is not the same dataset.")
    print(f"Persistence    : {t['persist_anom_c'].iloc[0]:+.2f} degC "
          f"(last season observed at the May-2026 init, carried forward).")
    print(f"Latest observed centered season: "
          f"{last_obs_date.date() if last_obs_date is not None else 'none'}  |  "
          f"verifiable target seasons: {n}\n")

    if n == 0:
        print("Nothing observed yet for the forecast's target seasons (a centered "
              "season needs its following month). Re-run monthly: the RISE phase "
              "(AMJ-JAS 2026) lands by ~Oct 2026; the OND peak not until ~Jan 2027.")
        return

    print("Aggregate error over verifiable seasons (skill = beating persistence & clim):")
    for label in ["cola", "persist", "clim"] + refs:
        e = scored[f"{label}_err"]
        print(f"  {label:8s}  MAE={e.abs().mean():.3f}  RMSE={_rmse(e):.3f}")

    print("\nPer-lead signed error, COLA minus obs (+ => COLA ran warm):")
    for _, r in scored.iterrows():
        flag = "  [provisional]" if r["provisional"] else ""
        print(f"  {r['target_season']}  lead={int(r['lead_months'])}m  "
              f"COLA={r['cola_anom_c']:.2f}  obs={r['obs_anom_c']:.2f}  "
              f"err={r['cola_err']:+.2f}{flag}")

    cola_rmse = _rmse(scored["cola_err"])
    print()
    for ref in ["persist", "clim"] + refs:
        ref_rmse = _rmse(scored[f"{ref}_err"])
        verb = "BEATS" if cola_rmse < ref_rmse else "loses to"
        print(f"  COLA {verb} {ref} by RMSE ({cola_rmse:.3f} vs {ref_rmse:.3f})")

    # sign test — the soundest small-sample statement about a one-sided (hot) model
    above = int((scored["obs_anom_c"] > scored["cola_anom_c"]).sum())
    lean = "COLA runs WARM vs obs" if above < n / 2 else "COLA runs COOL vs obs"
    print(f"\nSign test: obs sits above COLA in {above}/{n} seasons -> {lean} on this sample.")

    if n < MIN_N_FOR_CORR:
        print(f"\n[n={n} < {MIN_N_FOR_CORR}] Correlation suppressed - meaningless at "
              "this sample size. This is one ENSO event, one model run: read the "
              "per-lead error, not a 'validated / busted' verdict. See docs/validation.md.")


def main() -> int:
    t, loaded, last_obs_date = build_table()
    t.to_csv(OUT)
    summarize(t, loaded, last_obs_date)
    print(f"\nWrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
