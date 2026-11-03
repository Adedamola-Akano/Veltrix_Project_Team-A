# Veltrix Segmentation (Team A)

This project replaces one-size-fits-all selling with evidence about who Veltrix's customers really are. It profiles the customer data and works towards customer segments the business can act on.

## Repository contents

| Path | What it is |
|------|------------|
| `convert.py` | Converts the source Parquet files into CSV files |
| `csv_output/` | The converted CSV tables (stored with Git LFS) |
| `notebooks/01_data_extraction.ipynb` | Data extraction |
| `notebooks/02_profiling_duplicates_eda.ipynb` | Profiling, duplicate customers and exploratory analysis |

## Data

`csv_output/` contains 13 tables: agents, campaign_responses, campaigns, customers, interactions, leads, locations, payments, properties, property_views, site_visits, transactions and web_sessions.

The CSVs are large (`property_views.csv` is about 1 GB), so they are stored with [Git LFS](https://git-lfs.github.com/).

## Getting started

1. Install [Git LFS](https://git-lfs.github.com/), then run this once:
   ```bash
   git lfs install
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/Adedamola-Akano/Veltrix_Project_Team-A.git
   ```
3. Install the requirements:
   ```bash
   pip install [packages, e.g. pandas pyarrow jupyter]
   ```
4. To regenerate the CSVs from the Parquet files:
   ```bash
   python convert.py
   ```
   [Say where the Parquet files should be placed.]

## Working as a team

- Pull before you start: `git pull`
- Commit small, clear changes: `git add .` then `git commit -m "What you changed"`
- Push when done: `git push`
- Clear notebook outputs before committing if they show sensitive data.

## Team

[Names of team A members: Adedamola, Bamidele, Phillip, Jideofor, Basirat, Godwin and co.]

Supervisor materials are in a separate repository and are not included here.