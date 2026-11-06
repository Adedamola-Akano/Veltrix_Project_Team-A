# Veltrix segmentation: DS progress and decisions log

Status as of 6 November 2026. Built from the DA project plan (there is no separate DS plan).
Run order: `02` → `03` → `04` → `05` → `06` → `07`. All notebooks live in `notebooks/` and read only from `data/raw/` (02, 03) or `data/clean/` and `data/features/` (04 onward). The answer key (`_restricted/`) has never been opened.

## Status against the DA plan

| Plan step (DS part) | Notebook | Status |
|---|---|---|
| Day 1: convert Parquet to CSV | `convert.py` | Done (not needed by later steps) |
| Days 3-5: profile categoricals, find duplicates, EDA | `02_profiling_duplicates_eda` | Done |
| Day 4 (with DA): cleaning | `03_cleaning` | Done, all checks pass |
| Days 6-7: features, budget imputation, scaling, leakage check | `04_features` | Done, all checks pass |
| Day 8: baseline k-means | `05_clustering_baseline` | Done |
| Day 9: shortlist 2-3 candidate segmentations | `06_clustering_candidates` | Done. Lead candidate D, cross-check C |
| Day 10: stability, outcome test, `customer_segments` | `07_segments_validation` | Built, **not yet run on real data** |
| Day 11: segment statistics | `07_segments_validation` | Built, **not yet run on real data** |
| Day 12-13: persona cards, etc. | DA-led | Not started (needs agreed segment names) |
| Day 14: 6-week campaign test design | not started | Open |
| Day 15: scoring new customers, monthly refresh | not started | Open |
| Final scoring with `recoverability_check.py` | not run | Only when the model is final, once |

## Key decisions and why

**Cleaning (`03`)**
- Lead source: 28 spellings mapped to 14 channels (`cleaning_maps.py`). `Google` → Google Ads and `Website` → Veltrix website are **assumptions, to confirm with DA**.
- Country labels mapped to ISO codes; `is_overseas` agrees exactly with country (92,404 GB / 9,596 non-GB).
- Budget typos: purchase below £1,000 multiplied by 1,000 (entered in thousands); purchase at least 8x the median divided by 10; rent at least 5x the median divided by 10. Fixed 119 purchase rows (0.24%) and 54 rent rows (0.41%).
- Known limit: about 35-40 extra-zero typos on below-median purchase budgets cannot be told apart from genuine high budgets and are left unfixed. Report **median**, not mean, budgets per segment.

**Duplicates**
- 1,427 duplicates found (1.40% of 102,000), by shared email hash (1,103) or shared phone hash plus profile agreement (324). 98.5% / 98.8% of duplicates have exactly one lead, as the README describes.
- About 573 duplicates remain undetected (they changed both email and phone; there are no names or addresses). Customers: 102,000 → 100,573.

**EDA findings**
- Conversion of closed leads 18.2%, open leads 4.6%, March 2025 leads +42% on February (stamp duty), anonymous sessions 25%. All match the README.
- Median first-reply times differ in level from the README (27 / 234 minutes for senior / junior by first reply per lead; 54 / 466 across all interactions; README says 74 / 575). The senior-to-junior ratio is the same, so the pattern holds; the README's exact definition is unknown.
- `age_band` is 27.5% missing against the README's 18%. Unexplained.

**Features (`04`)**
- `property_views` holds View, Save, Virtual tour, Share and Floorplan download events. "What they look at" uses View only; the other types become engagement features.
- Leakage check (correlation with win rate): `n_interactions` (0.42) and `n_viewings` (0.34) excluded. Response time excluded because it measures the agent. Outcomes live in a separate table.
- `budget_missing` is kept as a feature (README: 20-70% missing by persona).

**Baseline (`05`)**
- k = 8 chosen from the README's eight personas and cluster interpretability, not from the curves (silhouette 0.22 at k=2, 0.12 or lower beyond). Stability between random starts 0.65.
- One baseline cluster (5.6%) was customers with no web sessions, an artefact of missing data. Fixed in `06`.

**Candidates (`06`)**

| Candidate | Smallest-largest | Stability (ARI) | Note |
|---|---|---|---|
| A: fixed k-means | 2.8-27.3% | 0.645 | Renters and buyers mix. Dropped |
| B: Gaussian mixture | 4.9-29.2% | 0.609 | Outlier (agreement 0.27-0.42). Dropped |
| C: k-prototypes | 2.8-20.8% | not measured | Agrees with D at 0.86. Cross-check |
| **D: two-stage k-means (split by Buy/Rent)** | 3.1-22.2% | **0.943** | **Lead candidate** |

D segments (provisional names): Downsizers 6.5%, Home movers 17.4%, Window shoppers 14.2%, First-time buyers 22.2%, Buy-to-let investors 12.1%, Overseas investors 6.8%, Corporate relocation lets 3.1%, Young renters 17.7%.

## Open items
1. Run `07` on real data; record the stability, conversion-test and PASS/CHECK results.
2. Edit `SHORTLIST` in `06` section 7 to `["D", "C"]` and re-run that cell.
3. Confirm with DA: the two lead-source mappings, the segment names, and that "views" means `event_type = 'View'`.
4. Share with DA: `cleaning_maps.py`, `duplicate_customer_map.csv`, `cleaning_log.csv`, `feature_dictionary.csv`, `labels_candidates.parquet`, `customer_segments`.
5. Day 14 campaign test design and Day 15 scoring/refresh design.
6. Final `recoverability_check.py` run, once, after the model is final.
