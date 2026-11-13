# Model card: segmentation seg-v1.0

**What it is.** Eight customer segments for Veltrix, built by a two-stage k-means: customers are first split by intent (Rent or Buy), then clustered inside each group (2 clusters for renters, 6 for buyers). New customers are scored by nearest cluster centre with every setting frozen (see `seg_scoring.py`).

**Built on.** 100,573 customers after removing duplicates; features from notebook 04 (60 numeric and 10 categorical, 142 columns in the model matrix). Created 2026-11-13.

**Segments (provisional names, to be confirmed with the DA team)**

| ID | Name | Share | Median budget (GBP) | Conversion (customers with a lead) |
|---|---|---|---|---|
| B0 | Downsizers | 6.5% | 382,500 | 33.0% |
| B1 | Home movers | 17.4% | 462,500 | 19.5% |
| B2 | Window shoppers | 14.2% | 335,000 | 8.5% |
| B3 | First-time buyers | 22.2% | 240,000 | 18.0% |
| B4 | Buy-to-let investors | 12.1% | 190,000 | 33.5% |
| B5 | Overseas investors | 6.8% | 585,000 | 17.0% |
| R0 | Corporate relocation lets | 3.1% | 2,800 | 45.8% |
| R1 | Young renters | 17.7% | 1,400 | 32.6% |

**How it was validated** (notebooks 06 and 07, at creation)
- Chosen over three other candidates on stability, separation and interpretability.
- Stability across 20 random 80% subsamples: overall ARI 0.90; every segment stable (Jaccard 0.77 to 1.00; window shoppers the weakest at 0.77).
- Segments differ on conversion: Cramer's V = 0.20 (small to medium).
- The answer key was not used to build or tune the model.

**Known limits**
- About 573 duplicate customers could not be detected and remain in the data (they changed both email and phone).
- About 35 to 40 extra-zero budget typos on below-median budgets cannot be separated from genuine high budgets.
- Window shoppers is the softest segment (borders first-time buyers). Corporate relocation lets is small (3.1%).
- Customers with no web sessions (about 5%) are placed on profile and enquiry features only.
- Segments describe behaviour and profile. Conversion differences are descriptive and do not prove a segment causes conversion.

**Do not** overwrite this version. If the model is rebuilt, call it seg-v1.1 and keep both.
