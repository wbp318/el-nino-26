# Methodology

How the raw series become aligned panels, and how to read the analysis.

## Resolution: monthly is primary

All three concepts exist at monthly resolution back to at least 1870, so **monthly**
is the primary modeling axis — the best balance of record length and signal. A
**yearly** panel is built as a secondary, long-baseline view (annual means of the
monthly drivers, plus native yearly sunspots back to 1700) for cycle-scale work such
as relating the ~11-year solar cycle to slow climate variability.

## Alignment

Each source is parsed into a tidy `Series` indexed by a **month-start `Timestamp`**
(`pandas.Timestamp(year, month, 1)`). The five monthly series are concatenated on a
single sorted `DatetimeIndex` spanning the union of their dates (1749-01 → present),
so every month is one row and missing values are explicit `NaN`. There is no
resampling or interpolation — values sit exactly where the providers report them.

The yearly panel groups the monthly drivers by calendar year (mean), then reindexes
onto the **union** of those years and the native yearly-sunspot years so the
pre-1749 sunspot-only years (1700–1748) survive.

### Season → month mapping (ONI)
ONI is published as 3-month running means labelled `DJF…NDJ`. Each label is placed at
its **center month**: `DJF`→January, `JFM`→February, …, `NDJ`→December. This makes
ONI a regular monthly series aligned with the others (each value is a smoothed,
centered anomaly rather than a single-month snapshot — relevant when interpreting
short lags).

## Two windows

A boolean **`clean_1950plus`** column marks the fully-instrumental era.

| Window | Span | Confidence | Use for |
|---|---|---|---|
| Clean | 1950 → present | High (instrumental) | Primary modeling, headline results |
| Long | ~1870 → present (monthly) | Mixed (pre-1950 reconstructed) | Length, robustness checks, cycle-scale |

**Why pre-1950 is lower confidence:** before 1950 the NAO is a two-station SLP index
(Lisbon − Iceland) rather than a gridded PC index, and ENSO is an SST
*reconstruction* (HadISST/ERSST) built from sparser ship observations. Relationships
estimated on the long window can therefore differ from the clean window — which is
exactly why `correlate.R` reports **both** side by side. Treat divergence between the
two as a signal about data quality, not necessarily about climate.

## Missing data

Handled at parse time, never silently filled:
- Sunspots: negative SN (`-1`) → `NaN`.
- Long Niño3.4: `-99.99` → `NaN`.
- Station NAO: `|v| ≥ 99` and ragged trailing months → omitted.

Correlations use **pairwise-complete** observations; the modeling step uses
**complete-case** rows over its chosen predictors + lags.

## Correlation & cross-correlation

`R/correlate.R` computes:
1. A **Pearson correlation matrix** across all driver columns, on each window.
2. **Lead/lag cross-correlations** (`ccf`, ±24 months) for the three conceptual
   pairs (NAO↔sunspots, ENSO↔sunspots, NAO↔ENSO), saved as PNGs, with the
   peak-|r| lag reported.

These are diagnostics — they confirm the parsers/alignment (e.g. the two NAO
measures and the two ENSO measures should strongly correlate) and surface candidate
lead/lag structure for the modeling step. They are **not** the project's result;
that awaits a target variable.

### Caveats when interpreting
- **Seasonality:** NAO and ENSO are winter-dominant; raw monthly correlation mixes
  seasons. A seasonal subset (e.g. DJFM) or seasonal anomalies may be more
  informative for a real target.
- **Autocorrelation:** all three series are highly autocorrelated (ONI is a 3-month
  mean; sunspots follow an 11-year cycle), so naive significance tests overstate
  confidence. Use block/seasonal resampling or effective-sample-size corrections
  before claiming significance.
- **Solar cycle:** the sunspot signal is dominated by the ~11-year cycle; any
  ENSO/NAO–solar link should be probed at cycle-relevant lags, not just 0–24 months.
