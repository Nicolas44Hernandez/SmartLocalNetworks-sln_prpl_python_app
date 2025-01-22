import joblib
import argparse
import pandas as pd
import numpy as np

pd.options.display.float_format = '{:.4f}'.format # Float display format

# Constants :
target_names = ['class 0 - 5Ghz - OFF', 'class 1 - 5Ghz - ON ']

parser = argparse.ArgumentParser(description='Model name')
parser.add_argument('model_name', type=str, help='Model name [MLP_C, XGBoost_C, LGBM_C]')
args = parser.parse_args()

model_name = args.model_name
models_dir = f"models/{model_name}"

# Test Model
print("---------------------------------------------------------------------------------------------------------------")
print(f"                                 {model_name} MODEL")
print("---------------------------------------------------------------------------------------------------------------")

print("Loading dataset ....")
# load datasets :
X_train = pd.read_csv(f"{models_dir}/X_train_{model_name}.csv")
y_train = pd.read_csv(f"{models_dir}/y_train_{model_name}.csv")
X_test = pd.read_csv(f"{models_dir}/X_test_{model_name}.csv")
y_test = pd.read_csv(f"{models_dir}/y_test_{model_name}.csv")
print("Dataset loaded")

print("Loading model")
# load model pipeline
model_save = f"{models_dir}/{model_name}_OPTIM.pkl"
model_pipeline = joblib.load(model_save)
print("Model loaded")

# on train dataset :
print("Predicions in train dataset...")
y_pred = model_pipeline.predict(X_train.values)
test_pred = model_pipeline.predict_proba(X_train.values)[:, 1]
print("Done")

# Write CLASSIFICATION Results on Train DATASET in csv file
print("Writting results in files [y_pred_train_dataset.csv, test_pred_train_dataset.csv]")
np.savetxt('y_pred_train_dataset.csv', y_pred, delimiter=',', fmt='%d')
np.savetxt('test_pred_train_dataset.csv', y_pred, delimiter=',', fmt='%d')
print("Done")

#On test dataset :
print("Predicions in test dataset...")
y_pred = model_pipeline.predict(X_test.values)
test_pred = model_pipeline.predict_proba(X_test.values)[:, 1]
print("Done")

# Write CLASSIFICATION Results on Test DATASET in csv file
print("Writting results in files [y_pred_test_dataset.csv, test_pred_test_dataset.csv]")
np.savetxt('y_pred_test_dataset.csv', y_pred, delimiter=',', fmt='%d')
np.savetxt('test_pred_test_dataset.csv', y_pred, delimiter=',', fmt='%d')
print("Done")
