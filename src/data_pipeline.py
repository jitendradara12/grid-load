import pandas as pd

NPP_PATH = "data/temp/npp_clean.csv"
ICED_PATH = "data/temp/iced_clean.csv"
SPLIT_TIME = "2025-12-30 12:00:00"


def get_iced_dataframe():
    iced_df = pd.read_csv(ICED_PATH)

    if iced_df.empty:
        print(f"Put ICED dataset in path: {ICED_PATH}\n")
        print("HINT: Run scripts/clean_datasets.py manually\n")
        exit()

    iced_df["datetime"] = pd.to_datetime(iced_df["datetime"])
    iced_df_filtered = iced_df[iced_df["datetime"] < SPLIT_TIME]

    return iced_df_filtered.sort_values("datetime")


def get_npp_dataframe():
    npp_df = pd.read_csv(NPP_PATH)

    if npp_df.empty:
        print(f"WARNING: NPP dataset is not available at {NPP_PATH}\n")
        print("Skipping merge...\n")
        return pd.DataFrame()

    npp_df["datetime"] = pd.to_datetime(npp_df["datetime"])
    npp_df = npp_df.resample("h", on="datetime")["value"].mean().reset_index()
    npp_df_filtered = npp_df[npp_df["datetime"] >= SPLIT_TIME]

    return npp_df_filtered.sort_values("datetime")


def get_train_dataframe():
    iced_df_filtered = get_iced_dataframe()
    npp_df_filtered = get_npp_dataframe()

    if not npp_df_filtered.empty:
        combined = (
            pd.concat([iced_df_filtered, npp_df_filtered])
            .sort_values("datetime")
            .reset_index(drop=True)
        )
    else:
        combined = iced_df_filtered

    combined["value"] = combined["value"].interpolate(method="linear").ffill().bfill()

    print(
        f"Combined time series spans from {combined['datetime'].min()} to {combined['datetime'].max()}."
    )
    print(f"Total hourly rows: {len(combined)}")

    return combined
