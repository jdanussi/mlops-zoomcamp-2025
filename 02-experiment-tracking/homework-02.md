# Homework 02 - Notes

## Virtual Environment

Create the conda virtual environment

```bash
conda create -n exp-tracking-env python=3.9

conda env list
# conda environments:
#
base                  *  /home/codespace/anaconda3
exp-tracking-env         /home/codespace/anaconda3/envs/exp-tracking-env
                         /opt/conda
```

Activate the environment

```bash
conda activate exp-tracking-env
(exp-tracking-env) @jdanussi ➜ /workspaces/mlops-zoomcamp-2025/02-experiment-tracking (main) $

which python
/home/codespace/anaconda3/envs/exp-tracking-env/bin/python

python -V
Python 3.9.21

pip list
Package    Version
---------- -------
pip        25.1
setuptools 78.1.1
wheel      0.45.1
```

Install dependencies

```bash
pip install mlflow jupyter scikit-learn pandas seaborn hyperopt xgboost

pip list | wc -l
81

mlflow --version
mlflow, version 2.22.0
```

--- 

## Download and preprocess the datasets

```bash
mkdir data
cd data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-02.parquet
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-03.parquet

cd ..
python preprocess_data.py --raw_data_path ./data --dest_path ./output

ls -l output/
total 7016
-rw-rw-rw- 1 codespace codespace  131004 May 19 19:14 dv.pkl
-rw-rw-rw- 1 codespace codespace 2458698 May 19 19:14 test.pkl
-rw-rw-rw- 1 codespace codespace 2374518 May 19 19:14 train.pkl
-rw-rw-rw- 1 codespace codespace 2215824 May 19 19:14 val.pkl
```

---

## MLflow Components

- mlflow ui: This is just the web UI — it starts a tracking server in read-only mode by default (i.e., it won't accept API calls like .log_param(), .start_run())

```bash
mlflow ui
```

- mlflow server: This starts the full MLflow tracking server (backend + UI + API) which can receive experiment logs, params, metrics, etc.

Start the MLflow tracking server locally with the defaults:

```bash
# Without setting the defaults explicitly
mlflow server

# Setting the defaults explicitly
mlflow server \
  --backend-store-uri ./mlruns \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000


mlflow server
[2025-05-23 14:49:32 -0300] [666279] [INFO] Starting gunicorn 23.0.0
[2025-05-23 14:49:32 -0300] [666279] [INFO] Listening at: http://127.0.0.1:5000 (666279)
[2025-05-23 14:49:32 -0300] [666279] [INFO] Using worker: sync
[2025-05-23 14:49:32 -0300] [666280] [INFO] Booting worker with pid: 666280
[2025-05-23 14:49:32 -0300] [666281] [INFO] Booting worker with pid: 666281
[2025-05-23 14:49:32 -0300] [666282] [INFO] Booting worker with pid: 666282
[2025-05-23 14:49:32 -0300] [666283] [INFO] Booting worker with pid: 666283
```

---

Start the MLflow tracking server locally with a sqlite backend-store `mlflow.db` and the non default artifact folder `./artifacts`:

```bash
mkdir artifacts
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./artifacts
 ```


## Answers

- Q1. Q1. Install MLflow: version 2.22.0
- Q2. Q2. Download and preprocess the data: 4
- Q3. Q3. Train a model with autolog: 2
- Q4. Launch the tracking server locally: default-artifact-root
- Q5. Tune model hyperparameters: 5.335
- Q6. Promote the best model to the model registry: 5.567