# Veltrix customer segments: Streamlit app

A read-only summary of the segmentation (model seg-v1.0). It reads **only aggregate files** from `app/data/`. It contains no customer-level data. Veltrix is a fictional agency and the data is synthetic.

## Run it on your computer
From the repo root (the `veltrix-segmentation_A` folder):

```powershell
pip install -r app/requirements.txt
python app/prepare_app_data.py
streamlit run app/streamlit_app.py
```

The browser opens at http://localhost:8501. `prepare_app_data.py` copies a fixed list of summary files from `notebooks/outputs/` and `models/seg-v1.0/` into `app/data/`. It never copies customer tables.

## Before anyone outside the team can see it
1. Get your supervisor's approval.
2. Check `app/data/` holds only the summary files listed by `prepare_app_data.py`. No `customer_segments`, `test_assignment`, features, outcomes, raw data or anything from `_restricted/`.
3. Decide where it is hosted. Streamlit Community Cloud deploys from a GitHub repository, so check the current rules for private repos and who can view an app. A small separate repo containing only `app/` is safer than the whole project repo.

## Updating it
After each monthly refresh: save the drift table as `notebooks/outputs/drift_latest.csv`, run `python app/prepare_app_data.py` again, and redeploy.
