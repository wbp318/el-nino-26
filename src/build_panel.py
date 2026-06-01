"""Parse the raw NAO / ENSO / sunspot files and align them into tidy panels.

Outputs (data/processed/):
  panel_monthly.csv  - primary modeling table, one row per month
  panel_yearly.csv   - secondary long-baseline table, one row per year

Both carry a `clean_1950plus` flag (the fully-instrumental window) and an empty
`target` column. Use merge_target() to drop a predictand in by date later.

Run:  python src/build_panel.py   (after src/fetch_data.py)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# 3-month ONI season label -> center month (DJF centers on Jan, ... NDJ on Dec)
_ONI_SEASONS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
                "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]
_ONI_CENTER = {s: i + 1 for i, s in enumerate(_ONI_SEASONS)}


def _month_start(year, month) -> pd.Timestamp:
    return pd.Timestamp(int(year), int(month), 1)


def parse_ssn_monthly() -> pd.Series:
    # cols: year;month;decimal_year;SNvalue;SNerror;Nobs;definitive
    df = pd.read_csv(RAW / "SN_m_tot_V2.0.csv", sep=";", header=None,
                     names=["y", "m", "dy", "sn", "err", "nobs", "defin"])
    sn = df["sn"].where(df["sn"] >= 0)  # -1.0 = missing
    idx = [_month_start(y, m) for y, m in zip(df["y"], df["m"])]
    return pd.Series(sn.values, index=pd.DatetimeIndex(idx), name="ssn_monthly")


def parse_ssn_yearly() -> pd.Series:
    # cols: decimal_year;SNvalue;SNerror;Nobs;definitive   (decimal_year like 1700.5)
    df = pd.read_csv(RAW / "SN_y_tot_V2.0.csv", sep=";", header=None,
                     names=["dy", "sn", "err", "nobs", "defin"])
    year = df["dy"].astype(float).astype(int)
    sn = df["sn"].where(df["sn"] >= 0)
    return pd.Series(sn.values, index=pd.Index(year, name="year"), name="ssn_yearly")


def parse_nao_cpc() -> pd.Series:
    # whitespace: year month value, from 1950
    df = pd.read_csv(RAW / "nao_cpc_monthly.ascii", sep=r"\s+", header=None,
                     names=["y", "m", "v"])
    idx = [_month_start(y, m) for y, m in zip(df["y"], df["m"])]
    return pd.Series(df["v"].values, index=pd.DatetimeIndex(idx), name="nao_cpc")


def parse_nao_station() -> pd.Series:
    # 2 header lines, then: YEAR Jan ... Dec (matrix). Last year may be ragged.
    lines = (RAW / "nao_station_monthly.txt").read_text().splitlines()[2:]
    recs = {}
    for ln in lines:
        parts = ln.split()
        if not parts or not parts[0].lstrip("-").isdigit():
            continue
        year = int(parts[0])
        for m, tok in enumerate(parts[1:13], start=1):
            v = float(tok)
            if abs(v) >= 99:  # sentinel for missing
                continue
            recs[_month_start(year, m)] = v
    s = pd.Series(recs, name="nao_station").sort_index()
    s.index = pd.DatetimeIndex(s.index)
    return s


def parse_oni() -> pd.Series:
    # SEAS YR TOTAL ANOM ; use ANOM, season -> center month
    df = pd.read_csv(RAW / "oni_cpc.ascii.txt", sep=r"\s+")
    months = df["SEAS"].map(_ONI_CENTER)
    idx = [_month_start(y, m) for y, m in zip(df["YR"], months)]
    return pd.Series(df["ANOM"].values, index=pd.DatetimeIndex(idx), name="enso_oni")


def parse_nino34_long() -> pd.Series:
    # line 1: "start end"; data: YEAR v1..v12; trailing metadata after data block
    lines = (RAW / "nino34_long_anom.data").read_text().splitlines()
    recs = {}
    for ln in lines[1:]:
        parts = ln.split()
        if len(parts) != 13 or not parts[0].isdigit() or len(parts[0]) != 4:
            continue  # stops cleanly at the trailing metadata lines
        year = int(parts[0])
        for m, tok in enumerate(parts[1:], start=1):
            v = float(tok)
            if v <= -99:  # -99.99 = missing
                continue
            recs[_month_start(year, m)] = v
    s = pd.Series(recs, name="enso_nino34").sort_index()
    s.index = pd.DatetimeIndex(s.index)
    return s


def merge_target(panel: pd.DataFrame, target: pd.Series) -> pd.DataFrame:
    """Drop a predictand into the `target` column by aligning on the index.

    `target` should be indexed by month-start Timestamps (monthly panel) or by
    integer year (yearly panel). Returns a new frame; the predictors are untouched.
    """
    out = panel.copy()
    out["target"] = target.reindex(out.index)
    return out


def build_monthly() -> pd.DataFrame:
    cols = [parse_nao_cpc(), parse_nao_station(), parse_oni(),
            parse_nino34_long(), parse_ssn_monthly()]
    df = pd.concat(cols, axis=1).sort_index()
    df.index.name = "date"
    df["clean_1950plus"] = df.index.year >= 1950
    df["target"] = pd.NA
    return df


def build_yearly() -> pd.DataFrame:
    m = build_monthly().drop(columns=["clean_1950plus", "target"])
    # annual means of the monthly drivers, keyed by integer year
    yearly = m.groupby(m.index.year).mean()
    ssn_y = parse_ssn_yearly()  # native yearly sunspots, back to 1700
    # extend the index so the pre-1749 sunspot-only years survive
    full = yearly.index.union(ssn_y.index)
    yearly = yearly.reindex(full)
    yearly.index.name = "year"
    yearly["ssn_yearly"] = ssn_y.reindex(full)
    yearly = yearly.drop(columns=["ssn_monthly"])
    yearly["clean_1950plus"] = yearly.index >= 1950
    yearly["target"] = pd.NA
    return yearly


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    monthly = build_monthly()
    yearly = build_yearly()

    monthly.to_csv(OUT / "panel_monthly.csv")
    yearly.to_csv(OUT / "panel_yearly.csv")

    def span(idx):
        return f"{idx.min()} .. {idx.max()}"

    print("panel_monthly.csv:", monthly.shape, "|", span(monthly.index))
    print("  non-null per column:")
    for c in monthly.columns:
        if c in ("clean_1950plus", "target"):
            continue
        s = monthly[c]
        first = s.first_valid_index()
        print(f"    {c:14s} n={s.notna().sum():>5}  first={first.date() if first is not None else '-'}")
    print("panel_yearly.csv :", yearly.shape, "|", f"{yearly.index.min()} .. {yearly.index.max()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
