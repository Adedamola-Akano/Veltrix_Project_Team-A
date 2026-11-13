# Monthly refresh runbook (seg-v1.0)

Owner: DS team, with the DA team for the checks. Time needed: about 30 minutes plus the data pull.

## Steps
1. **Get the new data.** Update the raw tables in `data/raw/` (or point the notebooks at the new extract). Do not edit the old files.
2. **Re-run the pipeline in order:** `02_profiling_duplicates_eda` (section B, to find new duplicates and save a fresh duplicate map), then `03_cleaning`, then `04_features`. Notebooks 02 and 03 stop with a message if there is a new lead source or country label: add it to `cleaning_maps.py` and re-run. Check that every PASS line still passes.
3. **Check data quality.** Load `customer_features.parquet` and run `seg_scoring.quality_report(raw, params)`. Any `FAIL` means **stop**. Find the cause before going further.
4. **Score everyone with the frozen model.** Load the model with `joblib.load("models/seg-v1.0/model.joblib")`, then `labels = seg_scoring.score(raw, bundle["params"])`. Do **not** re-fit the clusters.
5. **Check drift.** Run `seg_scoring.drift_table(labels, bundle["params"]["baseline_share"])`. An alert means a segment's share has moved by more than 20% (and more than the sampling noise).
6. **Check movement.** Compare each customer's new segment with last month's. Report how many customers changed segment and between which segments. Customers can move because their behaviour changed, which is expected. A very large movement is a warning.
7. **Publish.** Write `customer_segments` with the new labels, the segment names, `model_version = seg-v1.0` and the date. The DA team loads it into PostgreSQL and refreshes the dashboard.
8. **Keep the test clean.** Customers in the control group of the live campaign test must stay out of the audience lists (see `test_assignment.csv`).
9. **Log it.** Note the date, row counts, any FAIL or alert, and the decisions taken.

## When to rebuild the model (not just re-score)
- A drift alert in the same segment two months in a row, or
- a data quality change that is real and lasting (for example a new product line or a new lead source that matters), or
- a quarterly review, whichever comes first.
Rebuilding means going through notebooks 04 to 07 again and saving the result as **seg-v1.1**. Keep seg-v1.0 so results can be compared. Tell the DA team before the labels change.

## What this runbook does not cover
- **Re-fitting is not part of the monthly refresh**, by design. That is what keeps the segment names stable.
- **The answer key** is not used anywhere in the refresh.
