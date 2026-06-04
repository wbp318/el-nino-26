"""Seasonal & lagged correlation diagnostics for the NAO / sunspot -> ENSO question.

Operates on a cleaned ENSO / NAO / Sunspots workbook in the layout delivered by
the project's data provider (sheets: ENSO, NAO, Sunspots), and reports the three
diagnostics that matter for deciding the model's predictor structure:

  1. Seasonal cross-correlation - each predictor season (JFM/AMJ/JAS/OND) of year
     Y against ENSO's OND (peak) ONI of the same year.
  2. Sunspot lead - sunspot JFM of year Y-L against ENSO OND of year Y, L=0..3.
  3. ENSO persistence ("spring predictability barrier") - ONI of an early season
     against OND of the same year, which collapses across the boreal-spring barrier.

All correlations are Pearson r on annualised seasonal means over the overlapping
fully-instrumental window (1950+). Writes results/seasonal_lag_correlation.csv.

Run:  python src/seasonal_diagnostics.py --xlsx path/to/DataforElnino.xlsx
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "seasonal_lag_correlation.csv"

_ONI_SEASONS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
                "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]
_QUARTERS = {"JFM": [1, 2, 3], "AMJ": [4, 5, 6],
             "JAS": [7, 8, 9], "OND": [10, 11, 12]}


def _enso_seasonal(xl: pd.ExcelFile) -> pd.DataFrame:
    """ENSO ONI by year for the four standard quarters, from the raw monthly grid."""
    df = xl.parse("ENSO", header=0)
    df = df[df["YEAR"].notna()].copy()
    df["YEAR"] = df["YEAR"].astype(int)
    df = df.set_index("YEAR")
    return pd.DataFrame({q: df[ms].mean(axis=1)
                         for q, ms in {"JFM": ["DJF", "JFM", "FMA"],
                                       "AMJ": ["MAM", "AMJ", "MJJ"],
                                       "JAS": ["JJA", "JAS", "ASO"],
                                       "OND": ["SON", "OND", "NDJ"]}.items()})


def _monthly_grid_seasonal(xl: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    """Sunspots-style YEAR + JAN..DEC grid -> quarterly means by year."""
    df = xl.parse(sheet, header=0)
    df = df[df["YEAR"].notna()].copy()
    df["YEAR"] = df["YEAR"].astype(int)
    df = df.set_index("YEAR")
    mon = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
           "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    return pd.DataFrame({q: df[[mon[m - 1] for m in ms]].mean(axis=1)
                         for q, ms in _QUARTERS.items()})


def _nao_seasonal(xl: pd.ExcelFile) -> pd.DataFrame:
    """Tidy YEAR_MO / NAOI long series -> quarterly means by year."""
    df = xl.parse("NAO", header=0)
    df["d"] = pd.to_datetime(df["YEAR_MO"])
    df["y"], df["m"] = df["d"].dt.year, df["d"].dt.month
    df["NAOI"] = pd.to_numeric(df["NAOI"], errors="coerce")
    return pd.DataFrame({q: df[df["m"].isin(ms)].groupby("y")["NAOI"].mean()
                         for q, ms in _QUARTERS.items()})


def _r(a: pd.Series, b: pd.Series) -> tuple[float, int]:
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    return (round(d["a"].corr(d["b"]), 3), len(d))


def diagnostics(xlsx: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(xlsx)
    enso = _enso_seasonal(xl)
    ssn = _monthly_grid_seasonal(xl, "Sunspots")
    nao = _nao_seasonal(xl)

    rows: list[dict] = []
    for predictor, frame in (("sunspot", ssn), ("nao", nao)):
        for season in _QUARTERS:
            r, n = _r(frame[season], enso["OND"])
            rows.append({"diagnostic": "seasonal_vs_enso_ond",
                         "predictor": predictor, "detail": f"{season}@Y", "r": r, "n": n})
    for lead in range(4):
        r, n = _r(ssn["JFM"].shift(lead), enso["OND"])
        rows.append({"diagnostic": "sunspot_lead", "predictor": "sunspot",
                     "detail": f"JFM@Y-{lead}", "r": r, "n": n})
    for season in ("JFM", "AMJ", "JAS"):
        r, n = _r(enso[season], enso["OND"])
        rows.append({"diagnostic": "enso_persistence", "predictor": "enso",
                     "detail": f"{season}@Y", "r": r, "n": n})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--xlsx", required=True, type=Path,
                    help="cleaned ENSO/NAO/Sunspots workbook (provider layout)")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    table = diagnostics(args.xlsx)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out, index=False)
    print(table.to_string(index=False))
    print(f"\nwrote {args.out.relative_to(ROOT)}  ({len(table)} rows)")


if __name__ == "__main__":
    main()
