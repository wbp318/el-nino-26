"""Merge an annual crop-yield (or any yearly) predictand into panel_yearly.csv.

Scenario-B scaffolding: ENSO / NAO / sunspots are the features, USDA crop yield
is the target. This script is the plug-in point for whenever the USDA Crops
(and/or Weather) data lands — no code changes needed then, just a file.

Accepts either:
  --csv  data/targets/crop_yield.csv        two columns: year, value
  --xlsx DataforElnino.xlsx --sheet "USDA Crops"
         (provider workbook; the year column and first numeric value column
          are auto-detected, override with --year-col / --value-col)

Reads data/processed/panel_yearly.csv (run src/build_panel.py first), fills its
`target` column by year via build_panel.merge_target, and writes the panel back
in place. Re-running with a new file simply overwrites the target column;
predictors are never touched.

Run:  python src/merge_crop_target.py --csv data/targets/crop_yield.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from build_panel import merge_target

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / "data" / "processed" / "panel_yearly.csv"


def load_target_csv(path: Path, year_col: str | None = None,
                    value_col: str | None = None) -> pd.Series:
    """Read a two-column year,value CSV into a year-indexed Series."""
    df = pd.read_csv(path)
    return _to_series(df, year_col, value_col, source=str(path))


def load_target_xlsx(path: Path, sheet: str, year_col: str | None = None,
                     value_col: str | None = None) -> pd.Series:
    """Read a provider-workbook sheet into a year-indexed Series."""
    df = pd.read_excel(path, sheet_name=sheet)
    return _to_series(df, year_col, value_col, source=f"{path}[{sheet}]")


def _to_series(df: pd.DataFrame, year_col: str | None, value_col: str | None,
               source: str) -> pd.Series:
    if df.empty:
        raise ValueError(f"{source}: no rows")
    if year_col is None:
        candidates = [c for c in df.columns if str(c).strip().lower() == "year"]
        year_col = candidates[0] if candidates else df.columns[0]
    if value_col is None:
        numeric = [c for c in df.columns if c != year_col
                   and pd.api.types.is_numeric_dtype(df[c])]
        if not numeric:
            raise ValueError(f"{source}: no numeric value column found "
                             f"(columns: {list(df.columns)})")
        value_col = numeric[0]

    year = pd.to_numeric(df[year_col], errors="coerce")
    value = pd.to_numeric(df[value_col], errors="coerce")
    ok = year.notna() & value.notna()
    if not ok.any():
        raise ValueError(f"{source}: no usable (year, value) rows")
    s = pd.Series(value[ok].values,
                  index=pd.Index(year[ok].astype(int).values, name="year"),
                  name="target").sort_index()
    if s.index.has_duplicates:
        dupes = sorted(s.index[s.index.duplicated()].unique())
        raise ValueError(f"{source}: duplicate years {dupes}")
    return s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", type=Path, help="year,value CSV")
    src.add_argument("--xlsx", type=Path, help="provider workbook (.xlsx)")
    ap.add_argument("--sheet", default="USDA Crops",
                    help="workbook sheet name (with --xlsx)")
    ap.add_argument("--year-col", default=None, help="override year column name")
    ap.add_argument("--value-col", default=None, help="override value column name")
    args = ap.parse_args(argv)

    if not PANEL.exists():
        print(f"missing {PANEL} - run src/build_panel.py first")
        return 1

    if args.csv:
        target = load_target_csv(args.csv, args.year_col, args.value_col)
    else:
        target = load_target_xlsx(args.xlsx, args.sheet, args.year_col,
                                  args.value_col)

    panel = pd.read_csv(PANEL, index_col="year")
    merged = merge_target(panel, target)
    merged.to_csv(PANEL)

    n = merged["target"].notna().sum()
    yrs = merged.index[merged["target"].notna()]
    print(f"target: n={len(target)} years read, {n} matched panel rows "
          f"({yrs.min()}-{yrs.max()})")
    print(f"wrote {PANEL}")
    print("next: Rscript R/model.R  (note: model.R reads the MONTHLY panel; "
          "point it at panel_yearly.csv for an annual target)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
