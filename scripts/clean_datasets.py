import os
import sys
import pandas as pd

NPP_PATH = "data/demand_met_from_sep25.csv"
NPP_PATH_DEST = "data/temp/npp_clean.csv"
ICED_PATH = "data/temp/hourly_electricity_demand.csv"
ICED_PATH_DEST = "data/temp/iced_clean.csv"


def clean_npp_ds(NPP_PATH=NPP_PATH):
    print(f"Reading NPP from {NPP_PATH}...")
    npp_df = pd.read_csv(NPP_PATH)

    print("Cleaning NPP dataset...")
    npp_df["datetime"] = pd.to_datetime(npp_df["datetime"])

    npp_clean = npp_df[["datetime", "value"]].copy()

    npp_clean["value"] = npp_clean["value"].astype(float)

    return (
        npp_clean.sort_values("datetime")
        .drop_duplicates(subset=["datetime"])
        .reset_index(drop=True)
    )


def clean_iced_ds(ICED_PATH=ICED_PATH):
    print(f"Reading ICED from {ICED_PATH}...")
    iced_df = pd.read_csv(ICED_PATH)

    print("Cleaning ICED dataset...")

    iced_datetime = pd.to_datetime(
        iced_df["Year"].astype(str) + "-" + iced_df["Date"], format="%Y-%d-%b %I%p"
    )

    iced_clean = pd.DataFrame(
        {
            "datetime": iced_datetime,
            "value": iced_df["Hourly Demand Met (in MW)"].astype(float),
        }
    )
    return (
        iced_clean.sort_values("datetime")
        .drop_duplicates(subset=["datetime"])
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    arguments = sys.argv[1:]  # take npp iced or is_local

    if not arguments:
        arguments = ["npp", "iced"]

    if "npp" in arguments:
        npp_clean = clean_npp_ds()
        os.makedirs(os.path.dirname(NPP_PATH_DEST), exist_ok=True)
        print(f"Saving cleaned NPP to {NPP_PATH_DEST}...")
        npp_clean.to_csv(NPP_PATH_DEST, index=False)

    if "iced" in arguments:
        iced_clean = clean_iced_ds()
        os.makedirs(os.path.dirname(ICED_PATH_DEST), exist_ok=True)
        print(f"Saving cleaned ICED to {ICED_PATH_DEST}...")
        iced_clean.to_csv(ICED_PATH_DEST, index=False)

    print("Done cleaning datasets successfully!")
