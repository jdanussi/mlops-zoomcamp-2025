import os
import sys
import pandas as pd
import subprocess
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from batch import read_data


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


# Set env for localstack
os.environ['S3_ENDPOINT_URL'] = 'http://localhost:4566'

# Step 1: Create fake input data
data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
]
columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
df_input = pd.DataFrame(data, columns=columns)

# Step 2: Save to input bucket
input_file = 's3://nyc-duration/in/2023-01.parquet'
endpoint_url = os.getenv('S3_ENDPOINT_URL')

options = {
    'client_kwargs': {
        'endpoint_url': endpoint_url
    }
}

df_input.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)


# Step 3: Run batch.py
#subprocess.run(["python", "batch.py", "2023", "01"], check=True)

exit_code = os.system("python batch.py 2023 01")
if exit_code != 0:
    raise RuntimeError("Batch job failed")


# Step 4: Read output and verify
output_file = 's3://nyc-duration/out/2023-01.parquet'
df_result = read_data(output_file, endpoint_url)

print(df_result.head())

print("Sum of predicted_duration:", df_result['predicted_duration'].sum())
