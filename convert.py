import pandas as pd
from pathlib import Path

src = Path("veltrix-segmentation_A/data/raw/veltrix_medium")
out = Path("csv_output")
out.mkdir(exist_ok=True)

# Top-level files: one parquet -> one csv
for f in src.glob("*.parquet"):
    df = pd.read_parquet(f)
    df.to_csv(out / f"{f.stem}.csv", index=False)
    print("Converted", f.name, df.shape)

# Subfolders: combine all part files into one csv per folder
for folder in src.iterdir():
    if folder.is_dir() and folder.name != "_restricted":
        parts = sorted(folder.rglob("*.parquet"))
        if parts:
            df = pd.concat((pd.read_parquet(p)
                           for p in parts), ignore_index=True)
            df.to_csv(out / f"{folder.name}.csv", index=False)
            print("Converted folder", folder.name, df.shape)
