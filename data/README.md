# data/

Two subfolders, both **gitignored** (regenerable; sunspot data is CC BY-NC):

| Folder | Contents | Produced by |
|---|---|---|
| `raw/` | The 8 source files downloaded verbatim, + tracked `MANIFEST.md` (provenance). | `src/fetch_data.py` |
| `processed/` | `panel_monthly.csv`, `panel_yearly.csv` — the aligned modeling panels. | `src/build_panel.py` |

Only `raw/MANIFEST.md` and the `.gitkeep` placeholder are committed; everything else
is rebuilt by running the pipeline. See [`../docs/data-sources.md`](../docs/data-sources.md)
for what each source is and [`../docs/methodology.md`](../docs/methodology.md) for how
they're aligned.

## Panel schema (quick reference)

**`processed/panel_monthly.csv`** — one row per month, 1749→present:
`date`, `nao_cpc`, `nao_station`, `enso_oni`, `enso_nino34`, `ssn_monthly`,
`clean_1950plus`, `target`.

**`processed/panel_yearly.csv`** — one row per year, 1700→present: annual means of
the four monthly drivers + native `ssn_yearly`, plus `clean_1950plus`, `target`.

`target` is empty by design — the predictand slot (see
[`../docs/modeling.md`](../docs/modeling.md)).
