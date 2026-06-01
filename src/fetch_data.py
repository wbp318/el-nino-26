"""Download the raw NAO / ENSO / sunspot source files into data/raw/.

Each file is saved verbatim (no parsing here) so we keep provenance and can
re-parse without re-hitting the servers. build_panel.py does the parsing.

Run:  python src/fetch_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# label -> (url, local filename, one-line note)
SOURCES: dict[str, tuple[str, str, str]] = {
    # --- Sunspots: SILSO / WDC-SILSO, Royal Observatory of Belgium (CC BY-NC) ---
    "ssn_daily": (
        "https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.csv",
        "SN_d_tot_V2.0.csv",
        "Daily total sunspot number V2.0, 1818-present (semicolon CSV).",
    ),
    "ssn_monthly": (
        "https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv",
        "SN_m_tot_V2.0.csv",
        "Monthly mean total sunspot number V2.0, 1749-present.",
    ),
    "ssn_yearly": (
        "https://www.sidc.be/SILSO/DATA/SN_y_tot_V2.0.csv",
        "SN_y_tot_V2.0.csv",
        "Yearly mean total sunspot number V2.0, 1700-present.",
    ),
    # --- NAO ---
    "nao_cpc_monthly": (
        "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii",
        "nao_cpc_monthly.ascii",
        "CPC standardized monthly NAO index, 1950-present (year month value).",
    ),
    "nao_station_monthly": (
        "https://climatedataguide.ucar.edu/sites/default/files/2023-07/nao_station_monthly.txt",
        "nao_station_monthly.txt",
        "Hurrell station-based monthly NAO (NCAR CDG), 1865-present. NOTE: this "
        "snapshot is updated only through mid-2023 -- the long/reconstruction arm.",
    ),
    # --- ENSO ---
    "oni_cpc": (
        "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
        "oni_cpc.ascii.txt",
        "CPC Oceanic Nino Index (ONI), 1950-present (SEAS YR TOTAL ANOM).",
    ),
    "nino34_cpc_ersst5": (
        "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii",
        "nino34_cpc_ersst5.ascii",
        "CPC ERSSTv5 monthly Nino region SSTs incl. NINO3.4 + anomaly, 1950-present.",
    ),
    "nino34_long_anom": (
        "https://psl.noaa.gov/data/timeseries/month/data/nino34.long.anom.data",
        "nino34_long_anom.data",
        "NOAA PSL long Nino3.4 SST anomaly (ERSSTv5), 1870-present -- ENSO long arm.",
    ),
}


def fetch(label: str, url: str, fname: str) -> int:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    body = resp.content
    # Cheap guard: these endpoints sometimes serve an HTML error/wrapper page
    # instead of the data file. Catch that early rather than at parse time.
    head = body[:200].lstrip().lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
        raise RuntimeError(f"{label}: got an HTML page, not data ({url})")
    out = RAW / fname
    out.write_bytes(body)
    return len(body)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    failures = []
    for label, (url, fname, _note) in SOURCES.items():
        try:
            n = fetch(label, url, fname)
            print(f"  ok   {label:20s} {n:>9,} bytes -> {fname}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures.append((label, exc))
            print(f"  FAIL {label:20s} {exc}")
    if failures:
        print(f"\n{len(failures)} source(s) failed.", file=sys.stderr)
        return 1
    print(f"\nAll {len(SOURCES)} sources fetched into {RAW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
