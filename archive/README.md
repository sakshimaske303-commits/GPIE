# Archive

Development-time scratch scripts — one-off debugging (`debug_finland.py`), ad hoc data
inspection (`inspect_*.py`), a manual test of a single dataset filter (`merge_test.py`,
`refilter_gdp.py`), a partial retry helper (`retry_failed_ndvi.py`), and early API
smoke-tests written while getting each data source's auth/parsing working
(`test_auth.py`, `test_nuts.py`, `test_eurostat_gdp.py`, and the rest of the `test_*.py`
files here). None of these are imported by, or required to run, the actual pipeline —
kept for reference on how each data source was originally gotten working, not as
part of the reproducible workflow described in the main README.
