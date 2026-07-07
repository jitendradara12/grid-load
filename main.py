import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import train
import predict
from data_pipeline import get_npp_dataframe
from scripts.clean_datasets import clean_npp_ds


def run_prediction():
    df = get_npp_dataframe()
    if df.empty:
        df = (
            clean_npp_ds(NPP_PATH="data/demand_met_from_sep25.csv")
            .resample("h", on="datetime")["value"]
            .mean()
            .reset_index()
        )

    # last 24h actuals
    recent = df.tail(24)[["datetime", "value"]].copy()
    recent["datetime"] = recent["datetime"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    actuals = recent.rename(columns={"value": "demand_mw"}).to_dict(orient="records")

    # predict 48 hours
    preds = predict.predict_next_48h(df)
    preds["datetime"] = preds["datetime"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    forecasts = preds.rename(columns={"predicted_demand": "demand_mw"}).to_dict(orient="records")

    import json
    from datetime import datetime, timezone

    # ponytail: carry forward old predictions before overwriting
    json_path = "public/predictions/latest.json"
    prev_preds = []
    if os.path.exists(json_path):
        with open(json_path) as f:
            prev_preds = json.load(f).get("predictions", [])

    output = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "actuals": actuals,
        "predictions": forecasts,
        "previous_predictions": prev_preds,
    }

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(output, f)
    print(f"Wrote {len(actuals)} actuals + {len(forecasts)} predictions + {len(prev_preds)} prev")


def main():
    parser = argparse.ArgumentParser(description="Grid Demand Forecasting CLI")
    parser.add_argument(
        "action",
        choices=["train", "predict"],
        help="Action to perform: 'train' to train the model, 'predict' to run inference",
    )
    args = parser.parse_args()

    if args.action == "train":
        train.train_model()
    elif args.action == "predict":
        run_prediction()


if __name__ == "__main__":
    main()
