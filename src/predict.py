import pandas as pd

from scripts.clean_datasets import clean_npp_ds
from data_pipeline import get_npp_dataframe

# def predict_next_48h(df:pd.DataFrame) -> pd.DataFrame:
if __name__ == "__main__":
    df = clean_npp_ds()
    print(df.head())

    if df.empty:
        # run clean_datasets manually (most probably running in cloud)
        df = (
            clean_npp_ds(NPP_PATH="demand_met_from_sep25.csv")
            .resample("h", on="datetime")["value"]
            .mean()
            .reset_index()
        )
