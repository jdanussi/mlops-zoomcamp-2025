# Homework 02

conda create -n exp-tracking-env python=3.9

conda env list
# conda environments:
#
base                  *  /home/codespace/anaconda3
exp-tracking-env         /home/codespace/anaconda3/envs/exp-tracking-env
                         /opt/conda

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

pip install mlflow jupyter scikit-learn pandas seaborn hyperopt xgboost

pip list | wc -l
81

mlflow --version
mlflow, version 2.22.0

mkdir data
cd data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-02.parquet
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-03.parquet


cd ..
python preprocess_data.py --raw_data_path ./data --dest_path ./output


(exp-tracking-env) @jdanussi ➜ /workspaces/mlops-zoomcamp-2025/02-experiment-tracking (main) $ ls -l output/
total 7016
-rw-rw-rw- 1 codespace codespace  131004 May 19 19:14 dv.pkl
-rw-rw-rw- 1 codespace codespace 2458698 May 19 19:14 test.pkl
-rw-rw-rw- 1 codespace codespace 2374518 May 19 19:14 train.pkl
-rw-rw-rw- 1 codespace codespace 2215824 May 19 19:14 val.pkl


mlflow ui
mlflow ui --backend-store-uri sqlite:///mlflow.db

mkdir artifacts
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./artifacts
 



## Answers

- Q1. Q1. Install MLflow: version 2.22.0
- Q2. Q2. Download and preprocess the data: 4
- Q3. Q3. Train a model with autolog: 2
- Q4. Launch the tracking server locally: default-artifact-root
- Q5. Tune model hyperparameters:
- Q6. Promote the best model to the model registry: