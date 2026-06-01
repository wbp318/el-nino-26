# Raw data manifest

Retrieved **2026-06-01** by `src/fetch_data.py`. Files are saved verbatim from the
source; parsing happens in `src/build_panel.py`. Re-run the fetch script to refresh.

| File | Series | Range | Source URL |
|---|---|---|---|
| `SN_d_tot_V2.0.csv` | Sunspots, daily total (V2.0) | 1818→ | https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.csv |
| `SN_m_tot_V2.0.csv` | Sunspots, monthly mean (V2.0) | 1749→ | https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv |
| `SN_y_tot_V2.0.csv` | Sunspots, yearly mean (V2.0) | 1700→ | https://www.sidc.be/SILSO/DATA/SN_y_tot_V2.0.csv |
| `nao_cpc_monthly.ascii` | NAO, CPC standardized monthly | 1950→ | https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii |
| `nao_station_monthly.txt` | NAO, Hurrell station-based monthly | 1865→ (snapshot to mid-2023) | https://climatedataguide.ucar.edu/sites/default/files/2023-07/nao_station_monthly.txt |
| `oni_cpc.ascii.txt` | ENSO, CPC Oceanic Niño Index (ONI) | 1950→ | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt |
| `nino34_cpc_ersst5.ascii` | ENSO, CPC ERSSTv5 Niño3.4 + anom | 1950→ | https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii |
| `nino34_long_anom.data` | ENSO, NOAA PSL long Niño3.4 anomaly | 1870→ | https://psl.noaa.gov/data/timeseries/month/data/nino34.long.anom.data |

## Notes & licensing
- **Sunspots (SILSO):** CC BY-NC. Credit *WDC-SILSO, Royal Observatory of Belgium, Brussels*
  in any publication. Semicolon-separated; `-1` / `-1.0` are missing-value sentinels.
- **NAO station (NCAR CDG):** this is the long/reconstruction arm and the hosted snapshot only
  runs through ~June 2023. The CPC monthly NAO (1950→) is the live arm; use station NAO for
  pre-1950 length, CPC for currency.
- **Niño3.4 long (PSL):** anomalies vs 1981–2010 base; missing-value sentinel `-99.99`; the
  file has a few trailing metadata lines after the data block.
- **Common monthly overlap** across all three series ≈ **1870→present** (ENSO-limited once we
  use the long Niño3.4; 1865 if NAO-station-limited). Clean instrumental window = **1950→present**.
