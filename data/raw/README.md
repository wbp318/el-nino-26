# data/raw/

Source files downloaded **verbatim** by `src/fetch_data.py`. **Gitignored** (large +
CC BY-NC sunspot data); only this README and `MANIFEST.md` are tracked. Regenerate
with `python src/fetch_data.py`.

[`MANIFEST.md`](MANIFEST.md) is the authoritative provenance record (exact URL,
retrieval date, range, licensing per file).

| File | Series | Format |
|---|---|---|
| `SN_d_tot_V2.0.csv` | Sunspots, daily (V2.0) | semicolon CSV |
| `SN_m_tot_V2.0.csv` | Sunspots, monthly mean (V2.0) | semicolon CSV |
| `SN_y_tot_V2.0.csv` | Sunspots, yearly mean (V2.0) | semicolon CSV |
| `nao_cpc_monthly.ascii` | NAO, CPC monthly | whitespace `year month value` |
| `nao_station_monthly.txt` | NAO, Hurrell station-based | `YEAR Jan…Dec` matrix |
| `oni_cpc.ascii.txt` | ENSO, CPC ONI | `SEAS YR TOTAL ANOM` |
| `nino34_cpc_ersst5.ascii` | ENSO, CPC ERSSTv5 Niño regions | whitespace table |
| `nino34_long_anom.data` | ENSO, PSL long Niño3.4 anomaly | `YEAR v1…v12` grid |

Full format notes, missing-value sentinels, and citations:
[`../../docs/data-sources.md`](../../docs/data-sources.md).

> **Do not edit these by hand** — they are overwritten on every fetch. Parsing and
> cleaning happen in `src/build_panel.py`.
