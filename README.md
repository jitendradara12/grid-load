## Data

- **ICED** - hourly demand met, 2017 onwards. [Kaggle dataset by Harsh](https://www.kaggle.com/datasets/g0dbeast/hourly-electricity-demand)
- **NPP** - live demand data pulled from [npp.gov.in](https://npp.gov.in/dashBoard/gc-map-dashboard-meritchart), 4-minute granularity from Sep 2025. [Mirrored on Kaggle](https://www.kaggle.com/datasets/jitendradara12/demand-met-from-sep25)

## Usage
- get dependencies:
  ```
  uv sync
  ```
download datasets and match paths with the paths in src/data_pipeline.py
- clean datasets:
  ```
  uv run python scripts/clean_datasets.py
  ```
- train model:
  ```
  uv run python main.py train
  ```
- predict:
  ```
  uv run python main.py predict
  ```

Predictions are written to `public/predictions/latest.json` as a list of `{datetime, predicted_demand}` records.

## Automation

`.github/workflows/update.yml` runs daily:

1. pull latest NPP data
2. clean and merge
3. run inference
4. commit `latest.json`
5. push the updated dataset back to Kaggle

