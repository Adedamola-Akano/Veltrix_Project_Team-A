# Veltrix segmentation: DS progress and decisions log

Status as of 6 November 2026. Built from the DA project plan (there is no separate DS plan).
Run order: `02` → `03` → `04` → `05` → `06` → `07` → `08` → `09`. All notebooks live in `notebooks/` and read only from `data/raw/` (02, 03) or `data/clean/` and `data/features/` (04 onward). The answer key (`_restricted/`) has never been opened.

## Status against the DA plan

| Plan step (DS part) | Notebook | Status |
|---|---|---|
| Day 1: convert Parquet to CSV | `convert.py` | Done (not needed by later steps) |
| Days 3-5: profile categoricals, find duplicates, EDA | `02_profiling_duplicates_eda` | Done |
| Day 4 (with DA): cleaning | `03_cleaning` | Done, all checks pass |
| Days 6-7: features, budget imputation, scaling, leakage check | `04_features` | Done, all checks pass |
| Day 8: baseline k-means | `05_clustering_baseline` | Done |
| Day 9: shortlist 2-3 candidates | `06_clustering_candidates` | Done. Lead D, cross-check C |
| Day 10: stability, outcome test, `customer_segments` | `07_segments_validation` | Done, all checks pass |
| Day 11: segment statistics | `07_segments_validation` | Done |
| Day 12-13: persona cards, dashboard | DA-led | Needs the agreed segment names |
| Day 14: 6-week campaign test design | `08_campaign_test_design` | Done, all checks pass (see decision below) |
| Day 15: scoring new customers, monthly refresh, drift alert | `09_scoring_and_refresh` + `seg_scoring.py` | Built and tested on mock data; **to run on real data** |
| Final scoring with `recoverability_check.py` | not run | Only when the model is final, once |

## Key decisions and why

**Cleaning (`03`)**
- Lead source: 28 spellings mapped to 14 channels (`cleaning_maps.py`). `Google` → Google Ads and `Website` → Veltrix website are **assumptions, to confirm with DA**.
- Country labels mapped to ISO codes; `is_overseas` agrees exactly with country (92,404 GB / 9,596 non-GB).
- Budget typos: purchase below £1,000 multiplied by 1,000; purchase at least 8x the median divided by 10; rent at least 5x the median divided by 10. Fixed 119 purchase rows (0.24%) and 54 rent rows (0.41%).
- Known limit: about 35-40 extra-zero typos on below-median purchase budgets cannot be separated from genuine high budgets. Report **median**, not mean, budgets per segment.

**Duplicates**
- 1,427 duplicates found (1.40% of 102,000), by shared email hash (1,103) or shared phone hash plus profile agreement (324). 98.5% / 98.8% have exactly one lead, as the README describes.
- About 573 duplicates remain undetected (changed both email and phone; no names or addresses). Customers: 102,000 → 100,573.

**EDA findings**
- Conversion of closed leads 18.2%, open leads 4.6%, March 2025 leads +42% (stamp duty), anonymous sessions 25%. All match the README.
- Median first-reply times differ in level from the README (27 / 234 min by first reply per lead; 54 / 466 across all interactions; README 74 / 575). The senior-to-junior ratio is the same.
- `age_band` is 27.5% missing against the README's 18%. Unexplained.

**Features (`04`)**
- `property_views` holds View, Save, Virtual tour, Share and Floorplan download events. "What they look at" uses View only; the others become engagement features.
- Leakage check (correlation with win rate): `n_interactions` (0.42) and `n_viewings` (0.34) excluded. Response time excluded (it measures the agent). Outcomes live in a separate table.

**Baseline and candidates (`05`, `06`)**
- k = 8 chosen from the README's eight personas and interpretability, not from the curves (silhouette 0.22 at k=2, 0.12 or lower beyond). Baseline stability 0.65. One baseline cluster (5.6%) was customers with no web sessions, an artefact of missing data, fixed in `06`.

| Candidate | Smallest-largest | Stability (ARI) | Note |
|---|---|---|---|
| A: fixed k-means | 2.8-27.3% | 0.645 | Renters and buyers mix. Dropped |
| B: Gaussian mixture | 4.9-29.2% | 0.609 | Outlier. Dropped |
| C: k-prototypes | 2.8-20.8% | not measured | Agrees with D at 0.86. Cross-check |
| **D: two-stage k-means (Buy/Rent first)** | 3.1-22.2% | **0.943** | **Chosen: seg-v1.0** |

**Final segments, seg-v1.0 (`07`)**
- Stability over 20 subsamples: overall ARI 0.903. Segment Jaccard: young renters 1.00, corporate lets 0.998, overseas investors 0.976, buy-to-let 0.963, downsizers 0.953, home movers 0.946, first-time buyers 0.85, window shoppers 0.77 (weakest). All stable.
- Conversion differs by segment: chi-square 2,423, Cramer's V = 0.20.

| Segment (provisional name) | Share | Median budget | Conversion (with a lead) | Median days to decide |
|---|---|---|---|---|
| Corporate relocation lets | 3.1% | £2,800 pcm | 45.8% | 14 |
| Buy-to-let investors | 12.1% | £190k | 33.5% | 43 |
| Downsizers | 6.5% | £382k | 33.0% | 55 |
| Young renters | 17.7% | £1,400 pcm | 32.6% | 12 |
| Home movers | 17.4% | £462k | 19.5% | 71 |
| First-time buyers | 22.2% | £240k | 18.0% | 80 |
| Overseas investors | 6.8% | £585k | 17.0% | 71 |
| Window shoppers | 14.2% | £335k | 8.5% | 62 |

**Campaign test design (`08`)**
- No segment can detect a +35% lift in six weeks (baseline enquiry rates are only 1-4% per six weeks). The smallest detectable lifts: buy-to-let 37%, first-time buyers 38%, others 56% or more.
- Decision: test **buy-to-let investors** (the rule picked it), six weeks, `MAX_MDE = 40`. Primary KPI: enquiry rate (buyers take 43-80 days, longer than the test). Baseline 3.77%; a win is at least 5.16% (+37%) with p < 0.05. 3,511 customers per arm (need 3,443); arms balanced (largest standardised difference 0.03).
- A null result must be reported as **inconclusive**, not "the campaign does not work". To detect about 20-25%, a 12-week test would be needed.

**Scoring and refresh (`09`)**
- New customers are scored with the model **frozen**, by nearest cluster centre inside their intent group (`seg_scoring.py`); they are not re-clustered. Model and card saved in `models/seg-v1.0/`. Runbook and drift rule (20% relative change in segment share, beyond sampling noise) in `outputs/monthly_refresh_runbook.md`.

## Open items
1. Run `09` on real data; record the reproduction check, the held-out accuracy and the PASS/CHECK block.
2. Confirm with DA: the two lead-source mappings, the segment names, that "views" means `event_type = 'View'`, and the 6-week test choice (or a 12-week test).
3. Edit `SHORTLIST` in `06` section 7 to `["D", "C"]` and re-run that cell.
4. Share with DA: `cleaning_maps.py`, `duplicate_customer_map.csv`, `cleaning_log.csv`, `feature_dictionary.csv`, `customer_segments`, `segment_statistics.csv`, `test_assignment.csv` and the design file, `models/seg-v1.0/`.
5. Final `recoverability_check.py` run, once, after the model is final.
