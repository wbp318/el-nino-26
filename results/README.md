# results/

Analysis outputs written by `R/correlate.R`. **Gitignored** (regenerable); only this
README is tracked. Regenerate with `Rscript R/correlate.R`.

| File | Contents |
|---|---|
| `correlation_full.csv` | Pearson correlation matrix of all drivers, full record (~1749→). |
| `correlation_1950plus.csv` | Same, restricted to the clean 1950→present window. |
| `ccf_nao_cpc_vs_ssn_monthly.png` | Lead/lag cross-correlation, NAO vs sunspots (±24 mo). |
| `ccf_enso_oni_vs_ssn_monthly.png` | Lead/lag cross-correlation, ENSO vs sunspots. |
| `ccf_nao_cpc_vs_enso_oni.png` | Lead/lag cross-correlation, NAO vs ENSO. |

These are **diagnostics / sanity checks**, not the project's findings — the headline
result awaits a target variable (see [`../docs/modeling.md`](../docs/modeling.md)).
For how to read them and the caveats (seasonality, autocorrelation, solar cycle), see
[`../docs/methodology.md`](../docs/methodology.md).
