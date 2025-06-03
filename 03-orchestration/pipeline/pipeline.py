import pickle
from pathlib import Path

import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error

import mlflow


mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)


def read_dataframe(year, month):

    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)

    return df


def transform_dataframe(df):
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    return df


def create_X(df, dv=None):
    
    categorical = ['PULocationID', 'DOLocationID']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv


def train_model(X_train, y_train, X_val, y_val, dv):
    
    with mlflow.start_run() as run:
        
        lr = LinearRegression()
        
        mlflow.log_param("fit_intercept", lr.fit_intercept)
        mlflow.log_param("copy_X", lr.copy_X)
        mlflow.log_param("n_jobs", lr.n_jobs)
        mlflow.log_param("positive", lr.positive)
        mlflow.log_param("model_type", "linear_regression")
                
        lr.fit(X_train, y_train)
        print(f"Intercept of the model: {lr.intercept_:.2f}")

        y_pred = lr.predict(X_val)
        
        rmse = root_mean_squared_error(y_val, y_pred)
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("intercept", lr.intercept_)

        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
            
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        mlflow.sklearn.log_model(lr, artifact_path="models_mlflow")

        return run.info.run_id


def run(year, month):
    
    df_train = read_dataframe(year=year, month=month)

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(year=next_year, month=next_month)
    
    df_train = transform_dataframe(df_train)
    df_val = transform_dataframe(df_val)

    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values

    run_id = train_model(X_train, y_train, X_val, y_val, dv)
    print(f"MLflow run_id: {run_id}")
    return run_id

