# el-nino-26

Building a correlation / predictive model from three climate-driver time series:
**North Atlantic Oscillation (NAO)**, **El Niño–Southern Oscillation (ENSO)**, and
**sunspot number**. The three series are assembled as reusable predictors; a target
variable (a weather outcome, or another series) plugs in later without re-fetching.

## Data sources

All public and free. Raw files are downloaded by `src/fetch_data.py` into `data/raw/`
(not committed — see `.gitignore` and `data/raw/MANIFEST.md` for full provenance).

| Series | Variants pulled | Range |
|---|---|---|
| **Sunspots** (SILSO V2.0) | daily / monthly / yearly | 1818 / 1749 / 1700 → present |
| **NAO** | CPC standardized monthly; Hurrell station-based monthly | 1950→ ; 1865→ |
| **ENSO** | CPC ONI; CPC ERSSTv5 Niño3.4; NOAA PSL long Niño3.4 anomaly | 1950→ ; 1950→ ; 1870→ |

Two windows are produced so we can model on either without re-downloading:
- **Full / long record** — extends back as far as each source allows (overlap ≈ 1870→).
- **Clean 1950→present** — fully instrumental, highest confidence (flagged `clean_1950plus`).

Pre-1950 NAO is station-based and ENSO is SST-reconstructed: longer, but lower confidence.

## Layout

```
data/raw/         downloaded source files (gitignored) + MANIFEST.md
data/processed/   panel_monthly.csv, panel_yearly.csv (gitignored)
src/              fetch_data.py, build_panel.py        (Python pipeline)
R/                correlate.R, model.R                 (stats / modeling)
```

## Run

```bash
pip install -r requirements.txt
python src/fetch_data.py        # download raw sources -> data/raw/
python src/build_panel.py       # parse + align -> data/processed/*.csv
Rscript R/correlate.R           # correlation matrix + lead/lag cross-correlation
```

(On Windows, `Rscript` lives at `C:\Program Files\R\R-4.5.2\bin\Rscript.exe` if not on PATH.)

## Notes
- Sunspot data: **CC BY-NC** — credit *WDC-SILSO, Royal Observatory of Belgium, Brussels*.
- Target variable is intentionally undecided; `build_panel.py` exposes a `merge_target()`
  helper and an empty `target` column for whatever predictand we settle on.
