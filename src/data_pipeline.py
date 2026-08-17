import sys
from pathlib import Path
import pandas as pd

NPP_PATH = "data/temp/npp_clean.csv"
ICED_PATH = "data/temp/iced_clean.csv"
SPLIT_TIME = "2025-12-30 12:00:00"


def get_iced_dataframe():
    if not Path(ICED_PATH).exists():
        sys.exit(f"Put ICED dataset in path: {ICED_PATH}\n\nHINT: Run scripts/clean_datasets.py manually\n")

    df = pd.read_csv(ICED_PATH, parse_dates=["datetime"])
    if df.empty:
        sys.exit(f"Put ICED dataset in path: {ICED_PATH}\n\nHINT: Run scripts/clean_datasets.py manually\n")

    return df[df["datetime"] < SPLIT_TIME].sort_values("datetime")


def get_npp_dataframe():
    if not Path(NPP_PATH).exists():
        print(f"WARNING: NPP dataset is not available at {NPP_PATH}\n\nSkipping merge...\n")
        return pd.DataFrame()

    df = pd.read_csv(NPP_PATH, parse_dates=["datetime"])
    if df.empty:
        return pd.DataFrame()

    df = df.resample("h", on="datetime")["value"].mean().interpolate().ffill().bfill().reset_index()
    return df[df["datetime"] >= SPLIT_TIME].sort_values("datetime")


def get_train_dataframe():
    iced = get_iced_dataframe()
    npp = get_npp_dataframe()

    combined = (
        pd.concat([iced, npp], ignore_index=True).sort_values("datetime").reset_index(drop=True)
        if not npp.empty
        else iced
    )
    combined["value"] = combined["value"].interpolate().ffill().bfill()

    print(
        f"Combined time series spans from {combined['datetime'].min()} to {combined['datetime'].max()}."
    )
    print(f"Total hourly rows: {len(combined)}")

    return combined
