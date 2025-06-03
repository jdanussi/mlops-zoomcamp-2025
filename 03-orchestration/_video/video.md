
```bash
mkdir mlflow_data
cd mlflow_data
mlflow server \
    --backend-store-uri sqlite:///mlflow.db
```

```bash
python duration-prediction.py --year=2021 --month=1
/home/jdanussi/anaconda3/envs/exp-tracking-env/lib/python3.9/site-packages/xgboost/core.py:158: UserWarning: [20:35:11] WARNING: /workspace/src/objective/regression_obj.cu:227: reg:linear is now deprecated in favor of reg:squarederror.
  warnings.warn(smsg, UserWarning)
[0]     validation-rmse:11.44482
[1]     validation-rmse:10.77202
[2]     validation-rmse:10.18363
[3]     validation-rmse:9.67396
[4]     validation-rmse:9.23166
[5]     validation-rmse:8.84808
[6]     validation-rmse:8.51883
[7]     validation-rmse:8.23597
[8]     validation-rmse:7.99320
[9]     validation-rmse:7.78709
[10]    validation-rmse:7.61022
[11]    validation-rmse:7.45952
[12]    validation-rmse:7.33049
[13]    validation-rmse:7.22098
[14]    validation-rmse:7.12713
[15]    validation-rmse:7.04752
[16]    validation-rmse:6.98005
[17]    validation-rmse:6.92232
[18]    validation-rmse:6.87112
[19]    validation-rmse:6.82740
[20]    validation-rmse:6.78995
[21]    validation-rmse:6.75792
[22]    validation-rmse:6.72994
[23]    validation-rmse:6.70547
[24]    validation-rmse:6.68390
[25]    validation-rmse:6.66421
[26]    validation-rmse:6.64806
[27]    validation-rmse:6.63280
[28]    validation-rmse:6.61924
[29]    validation-rmse:6.60773
/home/jdanussi/anaconda3/envs/exp-tracking-env/lib/python3.9/site-packages/xgboost/core.py:158: UserWarning: [20:35:29] WARNING: /workspace/src/c_api/c_api.cc:1374: Saving model in the UBJSON format as default.  You can use file extension: `json`, `ubj` or `deprecated` to choose between formats.
  warnings.warn(smsg, UserWarning)
2025/05/29 20:35:39 WARNING mlflow.models.model: Model logged without a signature and input example. Please set `input_example` parameter when logging the model to auto infer the model signature.
🏃 View run resilient-hog-422 at: http://localhost:5000/#/experiments/1/runs/dc257bce99eb4904aac754bf05940e95
🧪 View experiment at: http://localhost:5000/#/experiments/1
MLflow run_id: dc257bce99eb4904aac754bf05940e95
```