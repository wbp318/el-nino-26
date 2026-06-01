# Glossary

Domain terms and acronyms used across the repo.

### NAO — North Atlantic Oscillation
A seesaw in atmospheric mass between the Icelandic Low and the Azores High,
measured as a normalized sea-level-pressure difference. Strongly influences winter
weather over the North Atlantic, Europe, and eastern North America. Positive phase:
stronger westerlies, milder/wetter northern Europe. Two variants here:
- **CPC NAO** — rotated-principal-component index from NOAA CPC, 1950→ (`nao_cpc`).
- **Station NAO (Hurrell)** — Lisbon − Iceland SLP difference, 1865→ (`nao_station`).

### ENSO — El Niño–Southern Oscillation
A coupled ocean–atmosphere oscillation in the tropical Pacific with global weather
teleconnections. **El Niño** = anomalously warm central/eastern equatorial Pacific;
**La Niña** = anomalously cool.

### ONI — Oceanic Niño Index
NOAA's operational ENSO index: the **3-month running-mean SST anomaly** in the Niño
3.4 region. El Niño/La Niña conditions are declared when ONI exceeds ±0.5 °C for
five consecutive overlapping seasons. Column `enso_oni`, 1950→.

### Niño 3.4 region
The equatorial Pacific box **5°N–5°S, 170°W–120°W**. Its SST anomaly is the most
common single ENSO indicator. The long reconstruction (`enso_nino34`, 1870→) is the
raw monthly Niño3.4 anomaly; ONI is its 3-month smoothed form.

### Niño 1+2 / 3 / 4
Other equatorial Pacific SST boxes (eastern → western). Present in the CPC ERSSTv5
file (`nino34_cpc_ersst5.ascii`) but not promoted to panel columns.

### SST — Sea Surface Temperature
Ocean skin temperature; the basis for ENSO indices. **Anomaly** = deviation from a
fixed base-period climatology (the long Niño3.4 uses 1981–2010).

### Sunspot number (SSN)
A count-based index of solar activity. The **International Sunspot Number**
(WDC-SILSO) follows the ~11-year solar cycle. **Version 2.0** is the 2015
re-calibration — values run ~⅓ higher than the legacy V1 series; never mix versions.
Columns `ssn_monthly` (1749→) and `ssn_yearly` (1700→).

### Predictor / target (predictand)
**Predictors** = inputs to the model (here NAO, ENSO, sunspots). **Target /
predictand** = the thing being predicted (undecided — the empty `target` column).

### Lead / lag, cross-correlation (CCF)
**Lag** = time offset between two series. **Cross-correlation** measures their
correlation across a range of lags; a peak at lag *k* suggests one series leads the
other by *k* steps. Computed by `R/correlate.R` (`ccf`, ±24 months).

### `clean_1950plus`
Boolean panel column: `True` for 1950→present, the fully-instrumental, highest-
confidence window. Pre-1950 data is reconstructed (station NAO, SST-based ENSO).

### ERSST / HadISST
Gridded historical SST reconstructions (NOAA Extended Reconstructed SST v5; UK Met
Office Hadley SST). They supply the pre-satellite ENSO record.

### Anomaly base period
The reference climatology that anomalies are measured against (e.g. 1981–2010 for
the long Niño3.4). Different products use different base periods — relevant when
comparing absolute anomaly values across sources.
