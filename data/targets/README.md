# data/targets/

Predictand (target) series waiting to be merged into the panels — the
Scenario-B plug-in point (climate drivers as features, crop yield as the
outcome). Files here **are** committed: they are small, provider-supplied, and
not regenerable from public fetches.

## Expected schema

A two-column CSV, one row per year:

```csv
year,value
1950,38.2
1951,36.9
```

- `year` — integer calendar year (matches `panel_yearly.csv`'s index).
- `value` — the yield / outcome number. Any header name works; the first
  numeric non-year column is used (override with `--value-col`).

`crop_yield_template.csv` is a header-only starter — copy it, fill it, and run:

```sh
python src/merge_crop_target.py --csv data/targets/crop_yield.csv
```

Or merge straight from the provider workbook once the USDA Crops sheet is
populated:

```sh
python src/merge_crop_target.py --xlsx DataforElnino.xlsx --sheet "USDA Crops"
```

Either path fills the `target` column of `data/processed/panel_yearly.csv`;
`R/model.R` then has a predictand to fit against.

## Open questions for the provider (as of 2026-07)

- Which crop(s), which measure (yield/bu-ac, production, price), which region?
- Annual is assumed; if the outcome is sub-annual, the monthly panel +
  `build_panel.merge_target` handles month-indexed series too.
