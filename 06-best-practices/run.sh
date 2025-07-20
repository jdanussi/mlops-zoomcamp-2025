#!/usr/bin/env bash

# Run unitary tests
pipenv run pytest tests/

# Run integration tests

# Export env variables
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566"
pipenv run python integration_tests/integration_test.py

