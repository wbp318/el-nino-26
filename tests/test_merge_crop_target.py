"""Hermetic tests for src/merge_crop_target.py (no network, no real panel)."""
import pandas as pd
import pytest

from merge_crop_target import _to_series, load_target_csv


def test_to_series_basic():
    df = pd.DataFrame({"year": [1950, 1951], "yield_bu_ac": [38.2, 36.9]})
    s = _to_series(df, None, None, source="t")
    assert list(s.index) == [1950, 1951]
    assert s.name == "target"
    assert s.loc[1951] == 36.9


def test_to_series_autodetects_year_by_position():
    # no column literally named "year": first column is assumed to be the year
    df = pd.DataFrame({"yr": [2000, 2001], "v": [1.0, 2.0]})
    s = _to_series(df, None, None, source="t")
    assert list(s.index) == [2000, 2001]


def test_to_series_drops_unparseable_rows_and_sorts():
    df = pd.DataFrame({"year": ["1951", "n/a", "1950"], "v": [1.0, 9.0, 2.0]})
    s = _to_series(df, None, None, source="t")
    assert list(s.index) == [1950, 1951]
    assert list(s.values) == [2.0, 1.0]


def test_to_series_rejects_duplicate_years():
    df = pd.DataFrame({"year": [1950, 1950], "v": [1.0, 2.0]})
    with pytest.raises(ValueError, match="duplicate years"):
        _to_series(df, None, None, source="t")


def test_to_series_rejects_no_numeric_column():
    df = pd.DataFrame({"year": [1950], "note": ["hi"]})
    with pytest.raises(ValueError, match="no numeric value column"):
        _to_series(df, None, None, source="t")


def test_load_target_csv_roundtrip(tmp_path):
    p = tmp_path / "crop.csv"
    p.write_text("year,value\n1950,38.2\n1951,36.9\n")
    s = load_target_csv(p)
    assert s.loc[1950] == 38.2


def test_merged_target_aligns_on_year(tmp_path):
    from build_panel import merge_target
    panel = pd.DataFrame({"ssn_yearly": [10.0, 20.0, 30.0], "target": pd.NA},
                         index=pd.Index([1949, 1950, 1951], name="year"))
    target = pd.Series([38.2], index=pd.Index([1950], name="year"))
    out = merge_target(panel, target)
    assert out.loc[1950, "target"] == 38.2
    assert pd.isna(out.loc[1949, "target"])
    assert pd.isna(panel.loc[1950, "target"])  # original untouched
