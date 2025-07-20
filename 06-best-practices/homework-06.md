# Homework 06 - Notes

## Setting the environment (the first time)

```bash
docker build -t ride-prediction .

docker run --rm -it -v "$(pwd)":/app -w /app ride-prediction 2023 03
predicted mean duration: 14.203865642696083

ls -ltr
total 22688
-rw-rw-r-- 1 jdanussi jdanussi    58548 jul 16 20:43  Pipfile.lock
-rw-rw-r-- 1 jdanussi jdanussi    17376 jul 16 20:43  model.bin
-rw-rw-r-- 1 jdanussi jdanussi      252 jul 16 20:44  Dockerfile
-rw-rw-r-- 1 jdanussi jdanussi      202 jul 16 20:45  Pipfile
-rw-r--r-- 1 root     root     23129111 jul 18 20:12 'taxi_type=yellow_year=2023_month=03.parquet'
-rw-rw-r-- 1 jdanussi jdanussi      436 jul 18 20:12  homework-06.md
-rw-rw-r-- 1 jdanussi jdanussi     1480 jul 18 20:13  batch.py



# Working from vitualenv
pipenv install
pipenv shell
python batch.py 2023 03
predicted mean duration: 14.203865642696083

pipenv install --dev pytest

AWS_ACCESS_KEY_ID=test \
AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3 mb s3://nyc-duration \
    --region us-east-1
make_bucket: nyc-duration

> aws --endpoint-url=http://localhost:4566 s3 ls
2025-07-19 15:42:18 nyc-duration






# Delete a file uploaded by mistake
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3 rm s3://nyc-duration/in/2023-03.parquet \
    --region us-east-1
delete: s3://nyc-duration/in/2023-03.parquet


AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3api put-object \
    --bucket nyc-duration \
    --key in/2021-01.parquet \
    --body data/yellow_tripdata_2021-01.parquet \
    --region us-east-1
{
    "ETag": "\"d2de0ffc4f9112b91c5fe3a407c07435\"",
    "ServerSideEncryption": "AES256"
}

AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3api put-object \
    --bucket nyc-duration \
    --key in/2021-02.parquet \
    --body data/yellow_tripdata_2021-02.parquet \
    --region us-east-1
{
    "ETag": "\"f01f2456ef459b33477ee73b4c2ced24\"",
    "ServerSideEncryption": "AES256"
}

AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3api put-object \
    --bucket nyc-duration \
    --key in/2021-03.parquet \
    --body data/yellow_tripdata_2021-03.parquet \
    --region us-east-1
{
    "ETag": "\"d40e6fe2f87ef06e2d94c23ca73dc491\"",
    "ServerSideEncryption": "AES256"
}

# List files in in/ folder
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3 ls s3://nyc-duration/in/ \
    --region us-east-1
2025-07-19 19:12:20   47673370 2023-01.parquet
2025-07-19 19:12:39   47748012 2023-02.parquet
2025-07-19 19:12:56   56127762 2023-03.parquet

# List files in out/ folder
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3 ls s3://nyc-duration/out/ \
    --region us-east-1


# Export env variables
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet" \
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet" \
export S3_ENDPOINT_URL="http://localhost:4566"

# To unset
unset INPUT_FILE_PATTERN \
unset OUTPUT_FILE_PATTERN \
unset S3_ENDPOINT_URL



python integration_test/save_dummy_data.py

# Delete the files for Jan/2023 in order to replace with the dummy data and his transform
WS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
aws --endpoint-url=http://localhost:4566 \
    s3 rm s3://nyc-duration/in/2023-03.parquet \
    --region us-east-1
delete: s3://nyc-duration/in/2023-03.parquet 


# Run all tests from bash (complete the task with Make file)
bash ./run.sh 
=================================================================== test session starts ===================================================================
platform linux -- Python 3.10.12, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/jdanussi/Documents/DataTalksClub/mlops-zoomcamp/mlops-zoomcamp-2025/06-best-practices
collected 1 item                                                                                                                                          

tests/test_batch.py .                                                                                                                               [100%]

==================================================================== 1 passed in 0.40s ====================================================================
input_file: s3://nyc-duration/in/2023-01.parquet
output_file: s3://nyc-duration/out/2023-01.parquet
endpoint_url: http://localhost:4566
   PULocationID  DOLocationID tpep_pickup_datetime tpep_dropoff_datetime
0           NaN           NaN  2023-01-01 01:01:00   2023-01-01 01:10:00
1           1.0           1.0  2023-01-01 01:02:00   2023-01-01 01:10:00
2           1.0           NaN  2023-01-01 01:02:00   2023-01-01 01:02:59
3           3.0           4.0  2023-01-01 01:02:00   2023-01-01 02:02:01
predicted mean duration: 18.138625226015364
     ride_id  predicted_duration
0  2023/01_0           23.197149
1  2023/01_1           13.080101
Sum of predicted_duration: 36.27725045203073
(base) jdanussi@jad-xps15:~/Documents/DataTalksClub/mlops-zoomcamp/mlops-zoomcamp-2025/06-best-practices$ 

```
---

## Answers

- Q1. Refactoring: f __name__ == '__main__':
- Q2. Installing pytest: __init__.py
- Q3. Writing first unit test: 2
- Q4. Mocking S3 with Localstack: --endpoint-url
- Q5. Creating test data: 3620 (3215 mi caso)
- Q6. Finish the integration test: 36.28
