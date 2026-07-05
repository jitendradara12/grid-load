import pandas as pd

NPP_PATH = "data/temp/npp_clean.csv"
ICED_PATH = "data/temp/iced_clean.csv"
npp_df = pd.read_csv(NPP_PATH)
iced_df = pd.read_csv(ICED_PATH)


if iced_df.empty:
    print(f"Put ICED dataset in path: {ICED_PATH}\n")
    exit()

if npp_df.empty:
    print(f"WARNING: NPP dataset is not available at {NPP_PATH}\n")
    print("Skipping merge...\n")
else:
    npp_df["datetime"] = pd.to_datetime(npp_df["datetime"])
    iced_df["datetime"] = pd.to_datetime(iced_df["datetime"])

    npp_df = npp_df.resample("h", on="datetime")["value"].mean().reset_index()

    # npp_df.set_index('datetime', inplace=True)
    # iced_df.set_index('datetime', inplace=True)

    SPLIT_TIME = "2025-12-30 12:00:00"

    iced_df_filtered = iced_df[iced_df["datetime"] < SPLIT_TIME]
    npp_df_filtered = npp_df[npp_df["datetime"] >= SPLIT_TIME]

    combined = (
        pd.concat([iced_df_filtered, npp_df_filtered])
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    combined["value"] = combined["value"].interpolate(method="linear").ffill().bfill()

    print(
        f"Combined time series spans from {combined['datetime'].min()} to {combined['datetime'].max()}."
    )
    print(f"Total hourly rows: {len(combined)}")


def get_train_dataframe():
    return combined
