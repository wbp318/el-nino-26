# docs/

Deep documentation for **el-nino-26**. The root [`README`](../README.md) is the
overview and quick start; these documents go into detail.

| Document | What it covers |
|---|---|
| [`data-sources.md`](data-sources.md) | Each of the 8 raw sources: provider, exact URL, file format, column layout, missing-value sentinels, historical range, update cadence, and citation. |
| [`methodology.md`](methodology.md) | How the series are aligned, choice of resolution, the long-vs-1950 windows, reconstruction confidence caveats, and how correlation / cross-correlation are computed. |
| [`pipeline.md`](pipeline.md) | Stage-by-stage walkthrough of `fetch_data.py` → `build_panel.py` → R scripts, how to refresh data, and how to extend the pipeline with a new source. |
| [`modeling.md`](modeling.md) | How to set the target variable, the `merge_target()` helper, `fit_model()` usage, lagged-predictor design, the time-ordered train/test split, and suggested next steps. |
| [`glossary.md`](glossary.md) | Definitions of every domain term and acronym used in the repo. |

## Reading order

New to the project? Read the root README, then `glossary.md`, then `data-sources.md`,
then `methodology.md`. If you are about to model, read `modeling.md`. If you are
maintaining or extending the code, read `pipeline.md`.
