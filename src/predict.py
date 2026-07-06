import pandas as pd
import pickle

from scripts.clean_datasets import clean_npp_ds
from data_pipeline import get_npp_dataframe
from features import features_main

MODEL_PATH = "models/demand_model.pkl"


def predict_next_48h(df: pd.DataFrame) -> pd.DataFrame:
    min_time = df["datetime"].min()
    required_rows = 337

    if len(df) < required_rows:  # add padding then
        pad_size = required_rows - len(df)

        pad_dates = pd.date_range(
            end=min_time - pd.Timedelta(hours=1), periods=pad_size, freq="h"
        )
        # Repeat the first value in the series to fill the pad
        pad_df = pd.DataFrame({"datetime": pad_dates, "value": df["value"].iloc[0]})
        # Combine pad and original df
        df = pd.concat([pad_df, df]).sort_values("datetime").reset_index(drop=True)

    X_pred, feature_names = features_main(df, is_training=False)

    with open(MODEL_PATH, "rb") as f:
        saved_data = pickle.load(f)
        model = saved_data["model"]
        saved_features = saved_data["feature_names"]

    # Align feature columns & training order
    X_pred = X_pred[saved_features]

    preds = model.predict(X_pred)[0]

    max_time = df["datetime"].max()
    pred_dates = pd.date_range(
        start=max_time + pd.Timedelta(hours=1), periods=48, freq="h"
    )
    return pd.DataFrame({"datetime": pred_dates, "predicted_demand": preds})


if __name__ == "__main__":
    df = get_npp_dataframe()

    if df.empty:
        # run clean_datasets manually (most probably running in cloud so the dataset will be at root)
        df = (
            clean_npp_ds(NPP_PATH="demand_met_from_sep25.csv")
            .resample("h", on="datetime")["value"]
            .mean()
            .reset_index()
        )

    print(predict_next_48h(df).head())
