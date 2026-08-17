import pandas as pd

LAGS = (*range(24), 47, 48, 71, 72, 167, 168, 335, 336)


def features_main(df: pd.DataFrame, is_training: bool = True):
    dt = df["datetime"].dt
    hour, dow, month = dt.hour, dt.dayofweek, dt.month
    is_weekend = dow.isin([5, 6]).astype(int)

    cols = {f"lag_{k}": df["value"].shift(k) for k in LAGS}
    cols["is_weekend"] = is_weekend
    cols |= {f"hour_{h}": (hour == h).astype(int) for h in range(1, 24)}
    cols |= {f"dayofweek_{d}": (dow == d).astype(int) for d in range(1, 7)}
    cols |= {f"month_{m}": (month == m).astype(int) for m in range(2, 13)}
    cols |= {f"hour_{h}_weekend": cols[f"hour_{h}"] * is_weekend for h in range(1, 24)}

    feature_names = list(cols)

    if is_training:
        target_names = [f"target_lead_{h}" for h in range(1, 49)]
        cols |= {col: df["value"].shift(-h) for h, col in enumerate(target_names, 1)}
        clean = pd.DataFrame(cols).dropna().reset_index(drop=True)
        return clean[feature_names], clean[target_names], feature_names

    feat_df = pd.DataFrame(cols, index=df.index)
    return feat_df.tail(1), feature_names
