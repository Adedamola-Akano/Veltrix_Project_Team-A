"""Copy ONLY the summary files the app needs into app/data/.

Run from the repo root:   python app/prepare_app_data.py

Safety: this uses an explicit allowlist of aggregate files. It never copies customer-level tables
(customer_segments, test_assignment, features, outcomes), the raw data, or anything from _restricted/.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
DEST = Path(__file__).resolve().parent / "data"
DEST.mkdir(exist_ok=True)

ALLOWED = [
    ROOT / "notebooks" / "outputs" / "segment_statistics.csv",
    ROOT / "notebooks" / "outputs" / "segment_baseline_shares.csv",
    ROOT / "notebooks" / "outputs" / "candidate_comparison.csv",
    ROOT / "notebooks" / "outputs" / "campaign_test_design.md",
    ROOT / "notebooks" / "outputs" / "monthly_refresh_runbook.md",
    # optional: written by the monthly refresh
    ROOT / "notebooks" / "outputs" / "drift_latest.csv",
    ROOT / "models" / "seg-v1.0" / "MODEL_CARD.md",
]

copied, missing = [], []
for src in ALLOWED:
    if src.exists():
        shutil.copy2(src, DEST / src.name)
        copied.append(src.name)
    else:
        missing.append(src.name)

print("Copied:", ", ".join(copied) or "nothing")
if missing:
    print("Not found (fine if optional):", ", ".join(missing))
