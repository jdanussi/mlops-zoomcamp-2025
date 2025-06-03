




You're on the right track by moving to **Airflow** for orchestrating this ML pipeline. To help you get started, here’s how to translate your current Python script into an Airflow DAG that:

* Downloads and preprocesses data.
* Trains a model.
* Logs everything in MLflow.
* Can recover from failures.
* Is structured with dependencies between tasks.

---

## ✅ Step-by-step Plan

1. **Split your script** into modular Python functions (which you already did).
2. **Set up an Airflow DAG** with PythonOperator tasks for:

   * Loading data.
   * Feature engineering.
   * Model training and MLflow logging.
3. Use **XComs** to pass values (like the trained model's `run_id`) between tasks.
4. Add Airflow **retries** and logging for resiliency.

---

## 🛠️ Example Airflow DAG

Here's a minimal `nyc_taxi_pipeline_dag.py` you can put into your `dags/` folder:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import pickle
from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
import mlflow

# MLflow setup
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True, parents=True)


def read_and_save_data(year, month, **context):
    df = read_dataframe(year, month)
    df.to_parquet(f"/tmp/df_train.parquet")

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(next_year, next_month)
    df_val.to_parquet(f"/tmp/df_val.parquet")


def read_dataframe(year, month):
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    df[['PULocationID', 'DOLocationID']] = df[['PULocationID', 'DOLocationID']].astype(str)
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    return df


def train_model(**context):
    df_train = pd.read_parquet("/tmp/df_train.parquet")
    df_val = pd.read_parquet("/tmp/df_val.parquet")

    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    y_train = df_train["duration"].values
    y_val = df_val["duration"].values

    run_id = run_training(X_train, y_train, X_val, y_val, dv)

    # Save run_id for downstream use
    context['ti'].xcom_push(key='mlflow_run_id', value=run_id)


def create_X(df, dv=None):
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv


def run_training(X_train, y_train, X_val, y_val, dv):
    with mlflow.start_run() as run:
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        best_params = {
            'learning_rate': 0.09585355369315604,
            'max_depth': 30,
            'min_child_weight': 1.060597050922164,
            'objective': 'reg:linear',
            'reg_alpha': 0.018060244040060163,
            'reg_lambda': 0.011658731377413597,
            'seed': 42
        }

        mlflow.log_params(best_params)

        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=30,
            evals=[(valid, 'validation')],
            early_stopping_rounds=50
        )

        y_pred = booster.predict(valid)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")

        return run.info.run_id


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="nyc_taxi_training_pipeline",
    default_args=default_args,
    description="Train and log NYC taxi model with MLflow",
    schedule_interval=None,  # Trigger manually or define as "0 12 1 * *" etc.
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["ml", "xgboost", "mlflow"],
) as dag:

    load_data = PythonOperator(
        task_id="load_data",
        python_callable=read_and_save_data,
        op_kwargs={"year": 2023, "month": 3},
    )

    train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    load_data >> train
```

---

## 🔄 Benefits of This Airflow Approach

* **Modular tasks**: easier to debug and retry individually.
* **XComs** for passing results (e.g., `run_id`).
* **Retry policy** for resilience.
* **MLflow integration** stays the same.

---

## 🧪 How to Run

1. Put this DAG in your `~/airflow/dags/` directory.
2. Run Airflow:

   ```bash
   airflow db init
   airflow scheduler &
   airflow webserver &
   ```
3. Trigger the DAG manually from the UI or set a cron schedule.

---

Would you like me to help you dockerize this with Airflow and MLflow running together for full reproducibility?



Great! Let’s break down your use case and build a **Dockerized Airflow setup** that runs your ML pipeline in **resilient, sequential tasks** and logs everything to **MLflow (also dockerized)**.

---

### ✅ Overview of the Architecture

You'll run:

* **Airflow**: to orchestrate your ML pipeline
* **MLflow Tracking Server**: to log metrics, params, and models
* **Volume-mapped workspace**: to persist models and run outputs

---

### 📁 Project Structure (recommended)

```
ml-pipeline/
├── airflow/
│   ├── dags/
│   │   └── train_pipeline_dag.py  # Airflow DAG
│   └── Dockerfile                 # Optional custom image
├── mlflow/
│   └── mlruns/                    # MLflow artifacts will be stored here
├── pipeline/
│   ├── __init__.py
│   └── pipeline.py                # Your Python logic here
├── docker-compose.yaml
└── requirements.txt              # Python dependencies
```

---

### 🚀 Step 1: `pipeline/pipeline.py` (Your original script, modularized)

Move your script logic into functions (you mostly already have them). Remove `argparse`, and make `run(year, month)` the callable from Airflow.

---

### 📦 Step 2: `docker-compose.yaml`

Here's a full example that runs **Airflow + MLflow + PostgreSQL (for MLflow backend store)**:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
      POSTGRES_DB: mlflow
    volumes:
      - postgres-data:/var/lib/postgresql/data

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    environment:
      BACKEND_STORE_URI: postgresql://mlflow:mlflow@postgres/mlflow
      ARTIFACT_ROOT: /mlflow/artifacts
    command: mlflow server \
      --backend-store-uri postgresql://mlflow:mlflow@postgres/mlflow \
      --default-artifact-root /mlflow/artifacts \
      --host 0.0.0.0
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow:/mlflow
    depends_on:
      - postgres

  airflow:
    image: apache/airflow:2.9.1
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__FERNET_KEY: your_fernet_key_here
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'false'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: sqlite:////usr/local/airflow/airflow.db
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./pipeline:/opt/airflow/pipeline
      - ./mlflow:/mlflow  # To share model artifacts
    ports:
      - "8080:8080"
    command: bash -c "airflow db init && airflow users create \
                      --username admin \
                      --firstname Firstname \
                      --lastname Lastname \
                      --role Admin \
                      --email admin@example.org \
                      --password admin && \
                      airflow scheduler & airflow webserver"
    depends_on:
      - mlflow

volumes:
  postgres-data:
```

---

### 🧠 Step 3: `airflow/dags/train_pipeline_dag.py`

This DAG breaks your pipeline into 3 main steps:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pipeline.pipeline import read_dataframe, create_X, train_model
import pandas as pd

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
        df.to_parquet(f"/tmp/train.parquet")
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        df_val = read_dataframe(next_year, next_month)
        df_val.to_parquet(f"/tmp/val.parquet")

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
        op_kwargs={'year': 2023, 'month': 1}
    )

    task2 = PythonOperator(
        task_id='prepare_features',
        python_callable=prepare_features
    )

    task3 = PythonOperator(
        task_id='train_model',
        python_callable=train
    )

    task1 >> task2 >> task3
```

---

### 📄 Step 4: `requirements.txt` (for ML + Airflow)

```text
pandas
xgboost
scikit-learn
mlflow
pyarrow
```

(You can pip install this inside Airflow's container if you're using a base image)

---

### ▶️ Step 5: Start everything

```bash
docker-compose up --build
```

* Airflow UI: [http://localhost:8080](http://localhost:8080) (user: `admin`, password: `admin`)
* MLflow UI: [http://localhost:5000](http://localhost:5000)

From Airflow UI, trigger `ml_training_pipeline`.

---

### ✅ Summary

This setup gives you:

* **Task resilience** (retry on failure, task-by-task monitoring)
* **Reproducibility** (Airflow + MLflow combo)
* **Docker isolation** for all services
* **Separation of concerns** between orchestration and model logic

Would you like me to generate the files (DAG + Docker + MLflow + pipeline) for you to download directly?


---

Great question — and you're absolutely right to spot this.

### ✅ Best Practice for Airflow + Custom Python Dependencies

Since the base image `apache/airflow:2.9.1` **does not include your ML/MLflow dependencies** (`xgboost`, `pandas`, `mlflow`, etc.), the **best practice** is:

> **Build a custom Airflow image using a `Dockerfile`** where you install all your `requirements.txt` dependencies during the image build step.

This ensures:

* Clean reproducibility
* Fast container startup
* No dependency installation at runtime
* Works with Airflow’s `LocalExecutor` or `CeleryExecutor` (if scaling later)

---

### ✅ How to Do It: Custom Airflow Dockerfile

Create `airflow/Dockerfile`:

```dockerfile
# Use official Airflow image as base
FROM apache/airflow:2.9.1

# Switch to root to install dependencies
USER root

# Install system packages if needed (e.g., for MLflow)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements and install Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
```

---

### ✅ Update `docker-compose.yaml` to Use Custom Build

Replace the `airflow` service like this:

```yaml
  airflow:
    build:
      context: .
      dockerfile: airflow/Dockerfile
    image: custom-airflow:latest
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__FERNET_KEY: your_fernet_key_here
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'false'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: sqlite:////usr/local/airflow/airflow.db
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./pipeline:/opt/airflow/pipeline
      - ./mlflow:/mlflow
    ports:
      - "8080:8080"
    command: bash -c "airflow db init && airflow users create \
                      --username admin \
                      --firstname Firstname \
                      --lastname Lastname \
                      --role Admin \
                      --email admin@example.org \
                      --password admin && \
                      airflow scheduler & airflow webserver"
    depends_on:
      - mlflow
```

Now Airflow will have:

* `mlflow`, `xgboost`, etc. installed via `requirements.txt`
* Your DAGs in `./airflow/dags`
* Your model code in `./pipeline`

---

### 🚫 Why Not Install at Runtime?

You *could* do:

```yaml
command: bash -c "pip install -r /requirements.txt && airflow webserver ..."
```

But that:

* Delays container startup every time
* Fails if there's no internet access
* Makes it harder to reproduce the environment exactly
* Breaks separation of build/run concerns in Docker

---

### ✅ Summary

| Option                                            | Pros                              | Cons                                |
| ------------------------------------------------- | --------------------------------- | ----------------------------------- |
| ✅ Custom Dockerfile (`pip install` at build time) | Fast, reproducible, clean         | Slightly more setup                 |
| ❌ Runtime `pip install` via `command`             | Fast to try, no Dockerfile needed | Fragile, slow startup, not scalable |

Let me know if you want me to scaffold the actual files (`Dockerfile`, `docker-compose.yaml`, and `requirements.txt`) for direct download.




Yes, you **should** create a `FERNET_KEY`. Here's why:

---

## 🔐 What is `FERNET_KEY` in Airflow?

The `FERNET_KEY` is used by Apache Airflow to **encrypt and decrypt sensitive data**, such as:

* Connection passwords (e.g., database credentials)
* Variable values (if marked as "encrypted")
* XCom values (depending on config)

This ensures that sensitive information stored in the Airflow metadata database isn't stored in plaintext.

---

## 🔧 Do I need to provide it?

Yes — if you don’t provide one explicitly, Airflow will generate a random key at runtime. But this means:

* If Airflow restarts with a **different key**, it won’t be able to decrypt any previously encrypted values (e.g., connections, variables).
* So, for **stable deployments**, you must provide a consistent `FERNET_KEY`.

---

## ✅ How to generate a Fernet key

You can generate one with Python:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Example output:

```
tKnY0ZGuQKaH6qAiWDhWozYkU6zOZWv9lEGQQrDkgZ4=
```

Copy this and add it to your `docker-compose.yaml`:

```yaml
environment:
  AIRFLOW__CORE__FERNET_KEY: tKnY0ZGuQKaH6qAiWDhWozYkU6zOZWv9lEGQQrDkgZ4=
```

Or, better: save it in an `.env` file and reference it from there for security and maintainability.

---

Let me know if you'd like help setting up `.env` file support in your Docker Compose setup.
