import pandas as pd
import numpy as np


def features_main(df, is_training=False):
    df = df.copy()
    new_cols = {}
    feature_cols = []

    lags = list(range(24)) + [47, 48, 71, 72, 167, 168, 335, 336]

    for lag in lags:
        col_name = f"lag_{lag}"
        new_cols[col_name] = df["value"].shift(lag)
        feature_cols.append(col_name)

    hour = df["datetime"].dt.hour
    dayofweek = df["datetime"].dt.dayofweek
    month = df["datetime"].dt.month
    is_weekend = dayofweek.isin([5, 6]).astype(int)

    new_cols["is_weekend"] = is_weekend

    for h in range(1, 24):
        new_cols[f"hour_{h}"] = (hour == h).astype(int)
    for d in range(1, 7):
        new_cols[f"dayofweek_{d}"] = (dayofweek == d).astype(int)
    for m in range(2, 13):
        new_cols[f"month_{m}"] = (month == m).astype(int)

    for h in range(1, 24):
        new_cols[f"hour_{h}_weekend"] = new_cols[f"hour_{h}"] * is_weekend

    time_cols = (
        [f"hour_{h}" for h in range(1, 24)]
        + [f"dayofweek_{d}" for d in range(1, 7)]
        + [f"month_{m}" for m in range(2, 13)]
        + [f"hour_{h}_weekend" for h in range(1, 24)]
    )

    all_features = feature_cols + ["is_weekend"] + time_cols

    if is_training:
        for h in range(1, 49):
            new_cols[f"target_lead_{h}"] = df["value"].shift(-h)
        new_df = pd.DataFrame(new_cols, index=df.index)
        df = pd.concat([df[["datetime", "value"]], new_df], axis=1)
        target_cols = [f"target_lead_{h}" for h in range(1, 49)]
        clean_df = df.dropna().reset_index(drop=True)
        return clean_df[all_features], clean_df[target_cols], all_features
    else:
        new_df = pd.DataFrame(new_cols, index=df.index)
        df = pd.concat([df[["datetime", "value"]], new_df], axis=1)
        # For prediction, return only the last row of features (the current t)
        return df.tail(1)[all_features], all_features
