# Data sources

Every series is pulled from an authoritative, public, free provider. `src/fetch_data.py`
downloads the raw files verbatim into `data/raw/`; this document describes what each
file *is*. Quick provenance (URL + retrieval date) also lives in
[`../data/raw/MANIFEST.md`](../data/raw/MANIFEST.md).

Raw files are **gitignored** — they are regenerable, large (daily sunspots ≈ 3 MB),
and the sunspot data carries a non-commercial license. Re-run the fetch script to
materialize them.

---

## 1. Sunspots — WDC-SILSO (Royal Observatory of Belgium)

The international sunspot number, **Version 2.0** (the 2015 re-calibration; values run
~⅓ higher than the old V1 series — do not mix versions).

| File | Series | Range | URL |
|---|---|---|---|
| `SN_d_tot_V2.0.csv` | Daily total | 1818→ | https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.csv |
| `SN_m_tot_V2.0.csv` | Monthly mean | 1749→ | https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv |
| `SN_y_tot_V2.0.csv` | Yearly mean | 1700→ | https://www.sidc.be/SILSO/DATA/SN_y_tot_V2.0.csv |

**Format:** semicolon-separated, no header.
- Monthly: `year ; month ; decimal_year ; SN ; SN_error ; N_obs ; definitive_flag`
- Yearly: `decimal_year ; SN ; SN_error ; N_obs ; definitive_flag` (decimal year ends in `.5`)
- Daily: `year ; month ; day ; decimal_year ; SN ; SN_error ; N_obs ; definitive_flag`

**Missing-value sentinel:** `-1` / `-1.0` in the SN column (mostly in sparse early
daily data). The parsers mask any negative SN to `NaN`.

**Update cadence:** monthly, around the start of each month (provisional values
firm up over subsequent months; `definitive_flag` = 1 once final).

**Citation / license:** **CC BY-NC.** "Source: WDC-SILSO, Royal Observatory of
Belgium, Brussels."

> Note: the `www.sidc.be/info/*csv.php` endpoints return an HTML page, not the CSV —
> always use the `/SILSO/DATA/` paths above.

---

## 2. North Atlantic Oscillation (NAO)

Two complementary measures are pulled — a *live* index and a *long historical* one.

### 2a. CPC standardized monthly NAO  *(live arm)*
| File | Range | URL |
|---|---|---|
| `nao_cpc_monthly.ascii` | 1950→ | https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii |

Rotated-PC-based index from NOAA's Climate Prediction Center, updated monthly.
**Format:** whitespace columns `year  month  value`.

### 2b. Hurrell station-based monthly NAO  *(long arm)*
| File | Range | URL |
|---|---|---|
| `nao_station_monthly.txt` | 1865→ (snapshot to mid-2023) | https://climatedataguide.ucar.edu/sites/default/files/2023-07/nao_station_monthly.txt |

Normalized sea-level-pressure difference between **Lisbon, Portugal** and
**Stykkishólmur/Reykjavík, Iceland** (NCAR Climate Data Guide, J. Hurrell).
**Format:** 2 header lines, then a `YEAR Jan…Dec` matrix; the final year may be
ragged (fewer than 12 values). Values `|v| ≥ 99` are treated as missing.

> The hosted snapshot only updates through ~June 2023. Use this arm for **length**
> (pre-1950 reach); use the CPC arm for **currency**. They correlate r ≈ 0.69.

---

## 3. El Niño–Southern Oscillation (ENSO)

Three measures — an official index, the underlying SST, and a long reconstruction.

### 3a. CPC Oceanic Niño Index (ONI)  *(the standard ENSO index)*
| File | Range | URL |
|---|---|---|
| `oni_cpc.ascii.txt` | 1950→ | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt |

3-month running-mean SST anomaly in the Niño 3.4 region; the index NOAA uses to
declare El Niño / La Niña. **Format:** `SEAS YR TOTAL ANOM`, where `SEAS` is a
3-month label (`DJF`,`JFM`,…,`NDJ`). The parser maps each label to its **center
month** (`DJF`→Jan … `NDJ`→Dec) and keeps `ANOM`.

### 3b. CPC ERSSTv5 Niño-region SSTs  *(raw SSTs incl. Niño3.4, 1991-2020 base)*
| File | Range | URL |
|---|---|---|
| `nino34_cpc_ersst5.ascii` | 1950→ | https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii |

Monthly SST + anomaly for Niño 1+2, 3, 4, and 3.4. **Format:** whitespace columns
`YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM` (the `ANOM` header repeats, so
parse the Niño3.4 anomaly by position — the last column). The anomalies use a **fixed
1991-2020** base period (hence `91-20` in the filename).

Promoted to the panel column **`enso_nino34_9120`** by `parse_nino34_ersst5()`. Its
fixed 1991-2020 base is the reason it — not `enso_oni` (sliding base) or `enso_nino34`
(1981-2010 base) — is the apples-to-apples truth series for forecast verification
against the IRI/CPC plume. See [`validation.md`](validation.md).

### 3c. NOAA PSL long Niño3.4 anomaly  *(long arm)*
| File | Range | URL |
|---|---|---|
| `nino34_long_anom.data` | 1870→ | https://psl.noaa.gov/data/timeseries/month/data/nino34.long.anom.data |

ERSSTv5/HadISST-based Niño3.4 SST anomaly extending back to 1870 — the arm that
sets the pre-1950 ENSO reach. **Format:** first line `start_year end_year`, then a
`YEAR v1…v12` grid, then a few trailing metadata lines (region, source, base
period). The parser keeps only 13-token lines whose first token is a 4-digit year,
which cleanly stops at the metadata. **Missing sentinel:** `-99.99`. Anomalies are
relative to the **1981–2010** base period.

---

## What ends up in the panels

| Panel column | From | Range |
|---|---|---|
| `nao_cpc` | 2a | 1950→ |
| `nao_station` | 2b | 1865→ |
| `enso_oni` | 3a | 1950→ |
| `enso_nino34` | 3c | 1870→ |
| `enso_nino34_9120` | 3b | 1950→ |
| `ssn_monthly` | 1 (monthly) | 1749→ |
| `ssn_yearly` (yearly panel) | 1 (yearly) | 1700→ |

`enso_nino34_9120` (from 3b, fixed 1991-2020 base) doubles as a QC cross-check against
the long series over 1950→ **and** as the base-matched truth series for forecast
verification — see [`validation.md`](validation.md).
