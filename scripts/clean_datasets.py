import os
import pandas as pd

NPP_PATH = "data/demand_met_from_sep25.csv"

ICED_PATH = "data/temp/hourly_electricity_demand.csv"

NPP_PATH_DEST = "data/temp/npp_clean.csv"
ICED_PATH_DEST = "data/temp/iced_clean.csv"

print(f"Reading NPP from {NPP_PATH}...")
npp_df = pd.read_csv(NPP_PATH)

print(f"Reading ICED from {ICED_PATH}...")
iced_df = pd.read_csv(ICED_PATH)

# Clean NPP
print("Cleaning NPP dataset...")
# Convert datetime column to datetime objects
npp_df["datetime"] = pd.to_datetime(npp_df["datetime"])
# Select and copy only datetime and value columns
npp_clean = npp_df[["datetime", "value"]].copy()
# Sort and drop duplicate timestamps
npp_clean = npp_clean.sort_values("datetime").drop_duplicates(subset=["datetime"]).reset_index(drop=True)

# Clean ICED
print("Cleaning ICED dataset...")
# Date format in ICED is e.g. "01-Jan 12am" combined with "Year"
iced_datetime = pd.to_datetime(
    iced_df["Year"].astype(str) + "-" + iced_df["Date"],
    format="%Y-%d-%b %I%p"
)
# Select datetime and the value column renamed to 'value'
iced_clean = pd.DataFrame({
    "datetime": iced_datetime,
    "value": iced_df["Hourly Demand Met (in MW)"]
})
# Sort and drop duplicate timestamps
iced_clean = iced_clean.sort_values("datetime").drop_duplicates(subset=["datetime"]).reset_index(drop=True)

# Ensure output directory exists
os.makedirs(os.path.dirname(NPP_PATH_DEST), exist_ok=True)
os.makedirs(os.path.dirname(ICED_PATH_DEST), exist_ok=True)

# Save cleaned datasets to CSV
print(f"Saving cleaned NPP to {NPP_PATH_DEST}...")
npp_clean.to_csv(NPP_PATH_DEST, index=False)

print(f"Saving cleaned ICED to {ICED_PATH_DEST}...")
iced_clean.to_csv(ICED_PATH_DEST, index=False)

print("Done cleaning datasets successfully!")
