"""Hermetic tests for the build_panel parsers — fixtures only, no network."""
import pandas as pd
import pytest

import build_panel as bp


def test_parse_nino34_ersst5_picks_nino34_anomaly_column(tmp_path, monkeypatch):
    """The Niño3.4 anomaly is the LAST column; the `ANOM` header repeats, so the
    parser must select by position, not name. April 2026 should read +0.23."""
    (tmp_path / "nino34_cpc_ersst5.ascii").write_text(
        " YR   MON  NINO1+2  ANOM   NINO3    ANOM   NINO4    ANOM   NINO3.4  ANOM\n"
        "2026   3   27.38    0.89   27.41    0.21   28.75    0.43   27.27   -0.01\n"
        "2026   4   26.80    1.27   27.95    0.37   29.40    0.77   28.05    0.23\n"
    )
    monkeypatch.setattr(bp, "RAW", tmp_path)

    s = bp.parse_nino34_ersst5()

    assert s.name == "enso_nino34_9120"
    assert list(s.index) == [pd.Timestamp(2026, 3, 1), pd.Timestamp(2026, 4, 1)]
    assert s.loc[pd.Timestamp(2026, 4, 1)] == pytest.approx(0.23)
    assert s.loc[pd.Timestamp(2026, 3, 1)] == pytest.approx(-0.01)


def test_parse_oni_maps_season_to_center_month(tmp_path, monkeypatch):
    """DJF centers on January, NDJ on December (the plume/ONI convention)."""
    (tmp_path / "oni_cpc.ascii.txt").write_text(
        "SEAS YR TOTAL ANOM\n"
        "DJF 2024 26.00 -0.37\n"
        "NDJ 2024 27.00 1.50\n"
    )
    monkeypatch.setattr(bp, "RAW", tmp_path)

    s = bp.parse_oni()

    assert s.loc[pd.Timestamp(2024, 1, 1)] == pytest.approx(-0.37)   # DJF -> Jan
    assert s.loc[pd.Timestamp(2024, 12, 1)] == pytest.approx(1.50)   # NDJ -> Dec


def test_parse_nino34_long_masks_missing_and_ignores_metadata(tmp_path, monkeypatch):
    """`-99.99` is missing (omitted); trailing non-data lines are ignored."""
    (tmp_path / "nino34_long_anom.data").write_text(
        "1870 2025\n"
        "2025 0.10 0.20 -99.99 0.40 0.50 0.60 0.70 0.80 0.90 1.00 1.10 1.20\n"
        " Nino3.4 ERSSTv5 anomaly, base period 1981-2010 -- metadata, not data\n"
    )
    monkeypatch.setattr(bp, "RAW", tmp_path)

    s = bp.parse_nino34_long()

    assert s.name == "enso_nino34"
    assert s.loc[pd.Timestamp(2025, 1, 1)] == pytest.approx(0.10)
    assert s.loc[pd.Timestamp(2025, 4, 1)] == pytest.approx(0.40)
    assert pd.Timestamp(2025, 3, 1) not in s.index   # -99.99 masked out
    assert len(s) == 11                              # 12 months minus the masked one


def test_merge_target_aligns_by_index_and_leaves_predictors(monkeypatch):
    idx = pd.date_range("2020-01-01", periods=3, freq="MS")
    panel = pd.DataFrame({"x": [1, 2, 3], "target": pd.NA}, index=idx)
    target = pd.Series([10.0], index=[pd.Timestamp(2020, 2, 1)], name="target")

    out = bp.merge_target(panel, target)

    assert pd.isna(out["target"].iloc[0])
    assert out["target"].iloc[1] == pytest.approx(10.0)
    assert pd.isna(out["target"].iloc[2])
    assert list(out["x"]) == [1, 2, 3]               # predictors untouched
    assert panel["target"].isna().all()              # original frame not mutated
