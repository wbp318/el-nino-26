"""Hermetic tests for verify_forecast — synthetic panel + forecast CSVs, no network."""
import pandas as pd
import pytest

import verify_forecast as vf


def _write_panel(tmp_path, monthly: dict):
    """Write a minimal panel CSV (date + enso_nino34_9120) and return its path."""
    df = pd.DataFrame({
        "date": pd.to_datetime(list(monthly.keys())),
        "enso_nino34_9120": list(monthly.values()),
    })
    p = tmp_path / "panel_monthly.csv"
    df.to_csv(p, index=False)
    return p


def _write_forecast(fdir, rows, base="1991-2020"):
    fdir.mkdir(exist_ok=True)
    lines = ["target_season,center_month_date,forecast_anom_c,base_period,lead_months"]
    for season, date, anom, lead in rows:
        lines.append(f"{season},{date},{anom},{base},{lead}")
    (fdir / "cola_ccsm4_may2026.csv").write_text("\n".join(lines) + "\n")


def test_observed_seasonal_is_centered_three_month_mean(tmp_path, monkeypatch):
    panel = _write_panel(tmp_path, {
        "2026-03-01": 0.0, "2026-04-01": 0.3, "2026-05-01": 0.6, "2026-06-01": 0.9,
    })
    monkeypatch.setattr(vf, "PANEL", panel)

    s = vf.observed_seasonal()

    # centered at Apr = mean(Mar, Apr, May) = (0.0 + 0.3 + 0.6)/3 = 0.3
    assert s.loc[pd.Timestamp(2026, 4, 1)] == pytest.approx(0.3)
    # centered at May = mean(0.3, 0.6, 0.9) = 0.6
    assert s.loc[pd.Timestamp(2026, 5, 1)] == pytest.approx(0.6)
    # ragged ends are NaN (min_periods=3)
    assert pd.isna(s.loc[pd.Timestamp(2026, 3, 1)])


def test_observed_seasonal_requires_the_column(tmp_path, monkeypatch):
    bad = tmp_path / "panel_monthly.csv"
    pd.DataFrame({"date": ["2026-01-01"], "enso_oni": [0.1]}).to_csv(bad, index=False)
    monkeypatch.setattr(vf, "PANEL", bad)
    with pytest.raises(SystemExit):
        vf.observed_seasonal()


def test_base_period_guard_rejects_mismatch(tmp_path, monkeypatch):
    fdir = tmp_path / "forecasts"
    _write_forecast(fdir, [("AMJ", "2026-05-01", 1.25, 0)], base="1981-2010")  # wrong base
    monkeypatch.setattr(vf, "FORECAST_DIR", fdir)
    with pytest.raises(SystemExit):
        vf.load_forecast("cola_ccsm4_may2026.csv")


def test_base_period_guard_accepts_match(tmp_path, monkeypatch):
    fdir = tmp_path / "forecasts"
    _write_forecast(fdir, [("AMJ", "2026-05-01", 1.25, 0)])
    monkeypatch.setattr(vf, "FORECAST_DIR", fdir)
    fc = vf.load_forecast("cola_ccsm4_may2026.csv")
    assert fc.loc[pd.Timestamp(2026, 5, 1), "forecast_anom_c"] == pytest.approx(1.25)


def test_build_table_per_lead_error_and_verifiable_flag(tmp_path, monkeypatch):
    # monthly obs through Jun 2026 -> centered May (AMJ) is verifiable; Jun (MJJ) is not
    panel = _write_panel(tmp_path, {
        "2026-02-01": -0.3, "2026-03-01": -0.1, "2026-04-01": 0.2,
        "2026-05-01": 0.5, "2026-06-01": 0.8,
    })
    fdir = tmp_path / "forecasts"
    _write_forecast(fdir, [("AMJ", "2026-05-01", 1.25, 0), ("MJJ", "2026-06-01", 1.75, 1)])
    monkeypatch.setattr(vf, "PANEL", panel)
    monkeypatch.setattr(vf, "FORECAST_DIR", fdir)
    monkeypatch.setattr(vf, "FORECASTS", {"cola": "cola_ccsm4_may2026.csv"})

    t, loaded, last = vf.build_table()

    amj = t.loc[pd.Timestamp(2026, 5, 1)]
    assert amj["obs_anom_c"] == pytest.approx(0.5)          # mean(0.2, 0.5, 0.8)
    assert amj["cola_err"] == pytest.approx(1.25 - 0.5)     # +0.75, ran warm
    assert bool(amj["verifiable"]) is True

    mjj = t.loc[pd.Timestamp(2026, 6, 1)]
    assert pd.isna(mjj["obs_anom_c"])                       # needs Jul -> not observed
    assert bool(mjj["verifiable"]) is False

    # climatology baseline is identically zero; persistence is frozen (a single value)
    assert (t["clim_anom_c"] == 0.0).all()
    assert t["persist_anom_c"].nunique() == 1


def test_summarize_runs_and_suppresses_correlation(tmp_path, monkeypatch, capsys):
    panel = _write_panel(tmp_path, {
        "2026-02-01": -0.3, "2026-03-01": -0.1, "2026-04-01": 0.2,
        "2026-05-01": 0.5, "2026-06-01": 0.8, "2026-07-01": 1.1,
    })
    fdir = tmp_path / "forecasts"
    _write_forecast(fdir, [("AMJ", "2026-05-01", 1.25, 0), ("MJJ", "2026-06-01", 1.75, 1)])
    monkeypatch.setattr(vf, "PANEL", panel)
    monkeypatch.setattr(vf, "FORECAST_DIR", fdir)
    monkeypatch.setattr(vf, "FORECASTS", {"cola": "cola_ccsm4_may2026.csv"})

    t, loaded, last = vf.build_table()
    vf.summarize(t, loaded, last)            # must not raise
    out = capsys.readouterr().out

    assert "Correlation suppressed" in out   # n < MIN_N_FOR_CORR
    assert "per-lead" in out.lower()
