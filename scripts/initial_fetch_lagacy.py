# data is already here so don't ping the servers again!
# comment it when needed
print("data is available in `data/` don't ping the poor servers _|_")
exit()


from datetime import datetime, timedelta
from pathlib import Path
import time
import pandas as pd
import requests
from tqdm import tqdm

BASE_URL = "https://npp.gov.in/dashBoard/demandmet1chartdata"

start_date = datetime(2025, 6, 25)
end_date = datetime(2026, 6, 25)
output_file = "data/demand_met_year.csv"

DAILY_DIR = Path("data/daily")
DAILY_DIR.mkdir(parents=True, exist_ok=True)

curr_date = start_date
dates = []
while curr_date <= end_date:
    dates.append(curr_date.strftime("%Y-%m-%d"))
    curr_date += timedelta(days=1)

print(f"Fetching data for {len(dates)} days...\n")

for st_date in tqdm(dates):
    daily_file = DAILY_DIR / f"demand_{st_date}.csv"

    if daily_file.exists():
        continue

    params = {"date": st_date}
    try:
        response = requests.get(BASE_URL, params=params, timeout=13)

        if response.status_code == 200:
            data = response.json()

            if not data:
                daily_file.touch()
                time.sleep(1.0)
                continue

            day_records = []
            for item in data:
                ts = item.get("updated_on")
                dt_object = datetime.fromtimestamp(ts / 1000) if ts else None

                day_records.append(
                    {
                        "formatted_date": st_date,
                        "timestamp": ts,
                        "datetime": dt_object,
                        "metric": item.get("name_of_data"),
                        "value": item.get("value_of_data"),
                    }
                )

            if day_records:
                day_df = pd.DataFrame(day_records)
                day_df.to_csv(daily_file, index=False)
        else:
            print(
                f"\n[Warning] Date {st_date} returned status code {response.status_code}"
            )

        time.sleep(0.69)

    except Exception as e:
        print(f"\n[Error] Failed to fetch {st_date}: {e}")
        continue

print("\nCompiling individual days into clean ML dataset...")
all_files = sorted(DAILY_DIR.glob("demand_*.csv"))

all_dfs = []
for f in all_files:
    if f.stat().st_size > 0:
        all_dfs.append(pd.read_csv(f))

if all_dfs:
    df = pd.concat(all_dfs, ignore_index=True)

    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df.drop_duplicates(subset=["datetime", "metric"]).reset_index(drop=True)

    df = df.sort_values(by="datetime").reset_index(drop=True)

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    print(f"\nSuccess! saved to {output_file}")
    print(f"Shape: {df.shape}")
else:
    print("\nNo data :(")
