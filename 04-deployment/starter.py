#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pickle
import pandas as pd


def read_data(year, month):
    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    
    df = pd.read_parquet(input_file)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    
    return df


def prepare_dictionaries(df):
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    dicts = df[categorical].to_dict(orient='records')
    
    return dicts


def load_model():
    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)
    
    return dv, model
    

def save_results(df, y_pred, year, month):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'output/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )
    return output_file


def apply_model(year, month):
    print(f'Reading the data for year {year:04d} and month {month:02d}...')
    df = read_data(year, month)
    dicts = prepare_dictionaries(df)
    
    print('Loading the model...')
    dv, model = load_model()
    
    print('Applying the model...')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)
    
    mean_pred = y_pred.mean()
    print(f"Mean predicted duration: {mean_pred:.2f}")

    print('Saving the results...')
    output_file = save_results(df, y_pred, year, month)
    
    return output_file


def run():
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    
    apply_model(year, month)


if __name__ == '__main__':
    run()

