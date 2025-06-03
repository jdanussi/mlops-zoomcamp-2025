# Homework 03 - Notes

## Setting the environment.

```bash
# Create folder to save model preprocess
mkdir -p ./models
chmod -R 777 ./models

# Create folder to log MLFlow artifacts
mkdir -p ./mlflow/artifacts
chmod -R 777 ./mlflow/artifacts

# Start the deployment
docker compose up --build
```

When all the containers are up and running enter Apache Airflow at http://localhost:8080 with 
- user: admin 
- password: admin 

and run the DAG `ml_training_pipeline`. Some answers to the questions are printed in the task logs.

After the DAG finished you can check the experiment `nyc-taxi-experiment` tracked with MLFlow at http://localhost:5000

---

## Answers

- Question 1. Select the Tool: Apache Airflow
- Question 2. Version: Version: v2.9.1
- Question 3. Creating a pipeline: 3,403,766
- Question 4. Data preparation: 3,316,216
- Question 5. Train a model: 24.77
- Question 6. Register the model: 4,534
