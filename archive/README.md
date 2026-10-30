# Archive

Development-time scratch scripts — one-off debugging (`debug_finland.py`), ad hoc data
inspection (`inspect_*.py`), a manual test of a single dataset filter (`merge_test.py`,
`refilter_gdp.py`), a partial retry helper (`retry_failed_ndvi.py`), and early API
smoke-tests written while getting each data source's auth/parsing working
(`test_auth.py`, `test_nuts.py`, `test_eurostat_gdp.py`, and the rest of the `test_*.py`
files here). None of these are imported by, or required to run, the actual pipeline —
kept for reference on how each data source was originally gotten working, not as
part of the reproducible workflow described in the main README.

## superseded_scripts/

Earlier versions of the pipeline, kept so the Development Log can be followed: the OData + HARP
Level-2 test pipeline (`run_pipeline.py`, `download_no2.py`, `extract_no2.py` and their helpers),
the single-mosaic acquisition for the expanded control group, the merge and model scripts that read
the superseded end-of-month NO₂ values, and the first single-cohort models. None of them is used by
the paper or by `reproduce_paper.py`.

## Moved here from the root

- `CONTROL_EXPANSION_README.md`: the run order used when the comparison group grew from three to nine countries. Historical; the current panel is built by `src/master_merge_control.py`.
- `GPIE_Executive_Summary.html`: an earlier HTML copy of the executive summary. The current one is `GPIE_Executive_Summary.md` / `.pdf` at the root.
