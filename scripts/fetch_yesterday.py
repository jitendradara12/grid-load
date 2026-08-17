from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys
import pandas as pd
import requests

BASE_URL = "https://npp.gov.in/dashBoard/demandmet1chartdata"
CSV_FILE = Path("data/demand_met_from_sep25.csv")
IST = timezone(timedelta(hours=5, minutes=30))
DATE = date.today() - timedelta(days=1)

if not CSV_FILE.exists():
    sys.exit(f"[Error] {CSV_FILE} not found. The Kaggle download step may have failed.")

try:
    resp = requests.get(BASE_URL, params={"date": DATE}, timeout=20)
    if resp.status_code != 200:
        sys.exit(f"[Error] API endpoint failed with status code: {resp.status_code}")
    data = resp.json()
except Exception as e:
    sys.exit(f"\n[Error] Failed to fetch or process data: {e}")

if not data:
    sys.exit(f"[Error] No data returned from API for {DATE}")

records = [
    {
        "formatted_date": DATE,
        "timestamp": item.get("updated_on"),
        "datetime": (
            datetime.fromtimestamp(item["updated_on"] / 1000, tz=IST).replace(
                tzinfo=None
            )
            if item.get("updated_on")
            else None
        ),
        "metric": item.get("name_of_data"),
        "value": item.get("value_of_data"),
    }
    for item in data
]

master_df = pd.read_csv(CSV_FILE)
day_df = pd.DataFrame(records)
combined = pd.concat([master_df, day_df], ignore_index=True)
initial_rows = len(combined)
combined.drop_duplicates(subset=["timestamp", "metric"], keep="last", inplace=True)
final_rows = len(combined)

if final_rows > len(master_df):
    combined.to_csv(CSV_FILE, index=False)
    print(f"Success: Appended {final_rows - len(master_df)} new rows for {DATE}.")
else:
    print(f"No new data to append for {DATE}.")

if (dupes := initial_rows - final_rows) > 0:
    print(
        f"Notice: Removed {dupes} duplicate rows (script likely ran multiple times today)."
    )
