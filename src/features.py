import pandas as pd


def features_main(df, is_training=True):
    df = df.copy()
    lags = list(range(24)) + [47, 48, 71, 72, 167, 168, 335, 336]
    new_cols = {f"lag_{lag}": df["value"].shift(lag) for lag in lags}
    hour = df["datetime"].dt.hour
    dayofweek = df["datetime"].dt.dayofweek
    month = df["datetime"].dt.month
    is_weekend = dayofweek.isin([5, 6]).astype(int)

    new_cols["is_weekend"] = is_weekend
    new_cols.update(
        {
            **{f"hour_{h}": (hour == h).astype(int) for h in range(1, 24)},
            **{f"dayofweek_{d}": (dayofweek == d).astype(int) for d in range(1, 7)},
            **{f"month_{m}": (month == m).astype(int) for m in range(2, 13)},
        }
    )
    new_cols.update(
        {
            f"hour_{h}_weekend": new_cols[f"hour_{h}"] * is_weekend
            for h in range(1, 24)
        }
    )
    all_features = list(new_cols)

    if is_training:
        targets = {f"target_lead_{h}": df["value"].shift(-h) for h in range(1, 49)}
        new_cols.update(targets)
        target_cols = [f"target_lead_{h}" for h in range(1, 49)]
    new_df = pd.DataFrame(new_cols, index=df.index)
    df = pd.concat([df[["datetime", "value"]], new_df], axis=1)

    if is_training:
        clean_df = df.dropna().reset_index(drop=True)
        return clean_df[all_features], clean_df[target_cols], all_features

    # For prediction, return only the last row of features (the current t)
    return df.tail(1)[all_features], all_features
