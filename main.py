import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.clean_datasets import clean_npp_ds
from src.data_pipeline import get_npp_dataframe
from src.predict import predict_next_48h
from src.train import train_model

JSON_PATH = Path("public/predictions/latest.json")


def load_npp_data():
    df = get_npp_dataframe()
    if df.empty:
        df = (
            clean_npp_ds(NPP_PATH="data/demand_met_from_sep25.csv")
            .resample("h", on="datetime")["value"]
            .mean()
            .reset_index()
        )
        df["value"] = df["value"].interpolate(method="linear").ffill().bfill()
    return df


def run_prediction():
    df = load_npp_data()

    recent = df.tail(24)
    actuals = [
        {"datetime": dt.strftime("%Y-%m-%dT%H:%M:%S"), "demand_mw": val}
        for dt, val in zip(recent["datetime"], recent["value"])
    ]

    preds = predict_next_48h(df)
    forecasts = [
        {"datetime": dt.strftime("%Y-%m-%dT%H:%M:%S"), "demand_mw": val}
        for dt, val in zip(preds["datetime"], preds["predicted_demand"])
    ]

    prev_preds = []
    if JSON_PATH.exists():
        with open(JSON_PATH) as f:
            prev_preds = json.load(f).get("predictions", [])

    output = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "actuals": actuals,
        "predictions": forecasts,
        "previous_predictions": prev_preds,
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w") as f:
        json.dump(output, f)

    print(
        f"Wrote {len(actuals)} actuals + {len(forecasts)} predictions + {len(prev_preds)} prev"
    )


def main():
    parser = argparse.ArgumentParser(description="Grid Demand Forecasting CLI")
    parser.add_argument(
        "action",
        choices=["train", "predict"],
        help="Action to perform: 'train' to train the model, 'predict' to run inference",
    )
    args = parser.parse_args()

    actions = {"train": train_model, "predict": run_prediction}
    actions[args.action]()


if __name__ == "__main__":
    main()
