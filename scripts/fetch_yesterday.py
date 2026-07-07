from datetime import date, datetime, timedelta
import sys
import pandas as pd
import requests
import os

BASE_URL = "https://npp.gov.in/dashBoard/demandmet1chartdata"
DATE = date.today() - timedelta(days=1)
params = {"date": DATE}

CSV_FILE = "data/demand_met_from_sep25.csv"

try:
    response = requests.get(BASE_URL, params=params, timeout=20)

    if response.status_code == 200:
        data = response.json()

        if not data:
            print(f"[Error] No data returned from API for {DATE}")
            sys.exit(1)
        else:
            day_records = []
            for item in data:
                ts = item.get("updated_on")
                dt_object = datetime.fromtimestamp(ts / 1000) if ts else None
                day_records.append(
                    {
                        "formatted_date": DATE,
                        "timestamp": ts,
                        "datetime": dt_object,
                        "metric": item.get("name_of_data"),
                        "value": item.get("value_of_data"),
                    }
                )

            if day_records:
                day_df = pd.DataFrame(day_records)

                if os.path.exists(CSV_FILE):
                    master_df = pd.read_csv(CSV_FILE)

                    combined_df = pd.concat([master_df, day_df], ignore_index=True)

                    initial_rows = len(combined_df)
                    combined_df.drop_duplicates(
                        subset=["timestamp", "metric"], keep="last", inplace=True
                    )
                    final_rows = len(combined_df)

                    combined_df.to_csv(CSV_FILE, index=False)

                    duplicates_removed = initial_rows - final_rows
                    print(f"Success: Appended {len(day_df)} rows for {DATE}.")
                    if duplicates_removed > 0:
                        print(
                            f"Notice: Removed {duplicates_removed} duplicate rows (script likely ran multiple times today)."
                        )
                else:
                    print(
                        f"[Error] {CSV_FILE} not found. The Kaggle download step may have failed."
                    )
                    sys.exit(1)

    else:
        print(f"[Error] API endpoint failed with status code: {response.status_code}")
        sys.exit(1)

except Exception as e:
    print(f"\n[Error] Failed to fetch or process data: {e}")
    sys.exit(1)
