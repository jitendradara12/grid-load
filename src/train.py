import os
import pickle
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_percentage_error
import data_pipeline

# import train and features models from src
from features import features_main

MODEL_SAVE_PATH = "models/demand_model.pkl"


def train_model():
    print("Loading datasets...\n")
    df = data_pipeline.get_train_dataframe()

    print("Building features...")
    X, y, feature_names = features_main(df, is_training=True)

    data_dates = df["datetime"].iloc[336 : len(df) - 48].reset_index(drop=True)

    # Train-Validation split
    # Train: data before 2026-04-01. Validation: 2026-04-01 onwards.
    train_mask = data_dates < "2026-04-01"
    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[~train_mask], y[~train_mask]

    print(f"Train samples: {len(X_train)}, Validation samples: {len(X_val)}")

    # Train and evaluate Ridge model on Validation set
    ridge_eval = Ridge(alpha=100.0)
    ridge_eval.fit(X_train, y_train)
    val_preds = ridge_eval.predict(X_val)

    val_mape = mean_absolute_percentage_error(y_val, val_preds)
    print(f"Validation MAPE (next 48h): {val_mape:.4%}")

    # Print MAPE for specific lead hours
    for h in [1, 12, 24, 36, 48]:
        lead_idx = h - 1
        h_mape = mean_absolute_percentage_error(
            y_val.iloc[:, lead_idx], val_preds[:, lead_idx]
        )
        print(f"  MAPE at t+{h:02d}h: {h_mape:.4%}")

    # Retrain on the complete dataset for production/serving
    print("Training final model on all data...")
    final_model = Ridge(alpha=100.0)
    final_model.fit(X, y)

    # Save model and feature names to models/
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    with open(MODEL_SAVE_PATH, "wb") as f:
        pickle.dump({"model": final_model, "feature_names": feature_names}, f)

    print(f"Model saved successfully to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train_model()
