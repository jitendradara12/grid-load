# data is already here so don't ping the servers again!
# comment it when needed
print("data is available in `data/` don't ping the poor servers _|_")
exit()


from datetime import datetime, timedelta
import time
import pandas as pd
import requests
from tqdm import tqdm

BASE_URL = "https://npp.gov.in/dashBoard/demandmet1chartdata"
start_date = datetime(2026,6,24)
end_date= datetime(2026,6,25)
output_file = "data/demand_met_year.csv"

all_records = []

curr_date = start_date
dates = []
while curr_date <= end_date:
    dates.append(curr_date.strftime("%Y-%m-%d"))
    curr_date += timedelta(days=1)

print("Fetching for ",len(dates), " days.....\n")

for st_date in tqdm(dates):
    params = {"date": st_date}
    try:
        response = requests.get(BASE_URL,params=params,timeout=13) #13 sec timeout for 1 request

        if response.status_code == 200:
            data = response.json()

            if data and isinstance(data,list):
                for item in data:
                    ts = item.get("updated_on")
                    if ts:
                        dt_object = datetime.fromtimestamp(ts/1000)
                    else:
                        dt_object = None

                        all_records.append(
                            {
                                "formatted_date": date_str,
                                "timestamp": ts,
                                "datetime": dt_object,
                                "metric": item.get("name_of_data"),
                                "value": item.get("value_of_data"),
                            }
                        )
        time.sleep(0.69)
    except Exception as e:
        print("Error fetching on ",st_date," ",e)
        continue


if all_records:
    df = pd.DataFrame(all_records)
    df = df.sort_values(by="datetime").reset_index(drop=True)
    df.to_csv(output_file, index=False)

    print("success. saved ",len(df)," rows to ", output_file)
else:
    print(all_records)
    print("no data:(")
