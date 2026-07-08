## Initializing

1. The best data yet is found on [npp](https://npp.gov.in/dashBoard/gc-map-dashboard-meritchart).
2. The api is unprocted and dumps json directly on `curl 'https://npp.gov.in/dashBoard/demandmet1chartdata?date=2026-06-08'`
3. The Endpoints served data all the way from sep25, my `scripts/fetch_yesterday` script runs everyday and updates the dataset with latest rows.
4. ICED dataset is longer and `scripts/clean_datasets.py` cleans and `src/data_pipeline.py` merges them to get
   Combined time series spans from 2017-01-01 00:00:00 to present.
5. Currently, using merged data for training and NPP dataset for inference.
6. TODO: By trial and error in google-colab, improve the training methods and accuracy.
