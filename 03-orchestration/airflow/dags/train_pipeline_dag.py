import sys
#sys.path.append('/opt/airflow')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pipeline.pipeline import read_dataframe, transform_dataframe, create_X, train_model
import pandas as pd

import pickle

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1
}

with DAG(
    dag_id="ml_training_pipeline",
    schedule_interval=None,
    default_args=default_args,
    catchup=False
) as dag:

    def load_data(**kwargs):
        year = kwargs['year']
        month = kwargs['month']
        df = read_dataframe(year, month)
        print(f"Raw training set: {len(df):,} records")  
        df.to_parquet(f"/tmp/train.parquet")
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        df_val = read_dataframe(next_year, next_month)
        df_val.to_parquet(f"/tmp/val.parquet")
    
    def transform_data():
        df_train = pd.read_parquet("/tmp/train.parquet")
        df_val = pd.read_parquet("/tmp/val.parquet")
        df_train = transform_dataframe(df_train)
        print(f"Transformed Training set: {len(df_train):,} records")  
        df_val = transform_dataframe(df_val)
        df_train.to_parquet("/tmp/train.parquet")
        df_val.to_parquet("/tmp/val.parquet")

    def prepare_features():
        df_train = pd.read_parquet("/tmp/train.parquet")
        df_val = pd.read_parquet("/tmp/val.parquet")
        X_train, dv = create_X(df_train)
        X_val, _ = create_X(df_val, dv)
        y_train = df_train['duration'].values
        y_val = df_val['duration'].values
        with open('/tmp/train_data.pkl', 'wb') as f:
            pickle.dump((X_train, y_train, X_val, y_val, dv), f)

    def train():
        with open('/tmp/train_data.pkl', 'rb') as f:
            X_train, y_train, X_val, y_val, dv = pickle.load(f)
        run_id = train_model(X_train, y_train, X_val, y_val, dv)
        with open('/tmp/run_id.txt', 'w') as f:
            f.write(run_id)

    task1 = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        op_kwargs={'year': 2023, 'month': 3}
    )

    task2 = PythonOperator(
            task_id='transform_data',
            python_callable=transform_data
    )

    task3 = PythonOperator(
        task_id='prepare_features',
        python_callable=prepare_features
    )

    task4 = PythonOperator(
        task_id='train_model',
        python_callable=train
    )

    task1 >> task2 >> task3 >> task4
