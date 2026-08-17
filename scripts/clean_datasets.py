import os
import sys
import pandas as pd

NPP_PATH = "data/demand_met_from_sep25.csv"
NPP_PATH_DEST = "data/temp/npp_clean.csv"
ICED_PATH = "data/temp/hourly_electricity_demand.csv"
ICED_PATH_DEST = "data/temp/iced_clean.csv"


def clean_npp_ds(NPP_PATH=NPP_PATH):
    print(f"Reading NPP from {NPP_PATH}...\nCleaning NPP dataset...")
    df = pd.read_csv(
        NPP_PATH,
        usecols=["datetime", "value"],
        parse_dates=["datetime"],
        dtype={"value": float},
    )
    return (
        df.sort_values("datetime")
        .drop_duplicates(subset=["datetime"])
        .reset_index(drop=True)
    )


def clean_iced_ds(ICED_PATH=ICED_PATH):
    print(f"Reading ICED from {ICED_PATH}...\nCleaning ICED dataset...")
    df = pd.read_csv(ICED_PATH)
    dt = pd.to_datetime(
        df["Year"].astype(str) + "-" + df["Date"], format="%Y-%d-%b %I%p"
    )
    clean = pd.DataFrame(
        {
            "datetime": dt,
            "value": df["Hourly Demand Met (in MW)"].astype(float),
        }
    )
    return (
        clean.sort_values("datetime")
        .drop_duplicates(subset=["datetime"])
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    arguments = sys.argv[1:] or ["npp", "iced"]
    os.makedirs("data/temp", exist_ok=True)

    if "npp" in arguments:
        npp_clean = clean_npp_ds()
        print(f"Saving cleaned NPP to {NPP_PATH_DEST}...")
        npp_clean.to_csv(NPP_PATH_DEST, index=False)

    if "iced" in arguments:
        iced_clean = clean_iced_ds()
        print(f"Saving cleaned ICED to {ICED_PATH_DEST}...")
        iced_clean.to_csv(ICED_PATH_DEST, index=False)

    print("Done cleaning datasets successfully!")
