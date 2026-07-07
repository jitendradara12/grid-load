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

    # predict 48 hours
    preds = predict.predict_next_48h(df)

    out_dir = "public/predictions"
    os.makedirs(out_dir, exist_ok=True)
    preds.to_json(f"{out_dir}/latest.json", orient="records", date_format="iso")
    print(preds)


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
