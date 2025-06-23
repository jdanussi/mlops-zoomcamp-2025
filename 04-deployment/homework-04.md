# Homework 04 - Notes

## Setting the environment (the first time)

```bash 
mkdir 04-deployment
cd 04-deployment
pipenv install scikit-learn==1.5.0 pandas pyarrow jupyter --python 3.10
pipenv shell
jupyter notebook
```

---

## Setting the environment (to repoduce)

```bash
# Change dir
cd 04-deployment

# Create the virtual env and install dependencies
pipenv install

# Activate the virtual env
pipenv shell

# Run the python script for April 2023
python starter.py 2023 4
Reading the data for year 2023 and month 04...
Loading the model...
Applying the model...
Mean predicted duration: 14.29
Saving the results...
```

---

## Building the docker image

```bash
# Build the image
docker build -t ride-duration-predictor .

# Run the container for May 2023
docker run ride-duration-predictor 2023 5
Reading the data for year 2023 and month 05...
Loading the model...
Applying the model...
Mean predicted duration: 0.19
Saving the results...
```

---

## Answers

- Q1. Notebook: 6.24
- Q2. Preparing the output: 66M
- Q3. Creating the scoring script: jupyter nbconvert --to script starter.ipynb
- Q4. Virtual environment: sha256:057b991ac64b3e75c9c04b5f9395eaf19a6179244c089afdebaad98264bff37c
- Q5. Parametrize the script: 14.29
- Q6. Docker container: 0.19
