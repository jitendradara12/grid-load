import pickle
import pandas as pd

from src.features import features_main

MODEL_PATH = "models/demand_model.pkl"


def predict_next_48h(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["value"] = df["value"].interpolate(method="linear").ffill().bfill()

    if len(df) < 337:
        pad_dates = pd.date_range(
            end=df["datetime"].min() - pd.Timedelta(hours=1),
            periods=337 - len(df),
            freq="h",
        )
        pad_df = pd.DataFrame({"datetime": pad_dates, "value": df["value"].iloc[0]})
        df = pd.concat([pad_df, df], ignore_index=True)

    X_pred, _ = features_main(df, is_training=False)

    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)

    preds = saved["model"].predict(X_pred[saved["feature_names"]])[0]
    pred_dates = pd.date_range(
        df["datetime"].max() + pd.Timedelta(hours=1), periods=48, freq="h"
    )
    return pd.DataFrame({"datetime": pred_dates, "predicted_demand": preds})


if __name__ == "__main__":
    from src.data_pipeline import get_npp_dataframe
    from scripts.clean_datasets import clean_npp_ds

    df = get_npp_dataframe()
    if df.empty:
        df = (
            clean_npp_ds(NPP_PATH="data/demand_met_from_sep25.csv")
            .resample("h", on="datetime")["value"]
            .mean()
            .reset_index()
        )
        df["value"] = df["value"].interpolate(method="linear").ffill().bfill()

    print(predict_next_48h(df).head())
