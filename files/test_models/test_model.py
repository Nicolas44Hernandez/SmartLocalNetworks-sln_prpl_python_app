import joblib
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

pd.options.display.float_format = '{:.4f}'.format # Float display format


parser = argparse.ArgumentParser(description='Model args')
parser.add_argument('model_name', type=str, help='Model name [MLP_2_C, MLP_12_3]')
parser.add_argument('model_dir', type=str, help='Model dir', default="models/")
args = parser.parse_args()

model_name = args.model_name
model_dir = args.model_dir
model_dir = f"{model_dir}/{model_name}"

def compute_accuracy(list1, list2):
    # Ensure both lists are of the same length
    if len(list1) != len(list2):
        raise ValueError("Lists must be of the same length to compute accuracy.")

    # Count matching elements
    matches = sum(1 for a, b in zip(list1, list2) if a == b)

    # Calculate accuracy percentage
    accuracy = (matches / len(list1)) * 100
    return accuracy

# Test Model
print("---------------------------------------------------------------------------------------------------------------")
print(f"                                 {model_name} MODEL")
print("---------------------------------------------------------------------------------------------------------------")


# Load model
print("Loading model")
model_file = f"{model_dir}/{model_name}_OPTIM.pkl"
model = joblib.load(model_file)
print("Model loaded")


# Load data
print("Loading dataset ....")
X_test = pd.read_csv(f"{model_dir}/X_test.csv")
y_test = pd.read_csv(f"{model_dir}/y_test.csv")
# Load the original lists to evaluate predictions
y_pred_proba_original = pd.read_csv(f"{model_dir}/y_pred_proba.csv")
y_pred_original = pd.read_csv(f"{model_dir}/y_pred.csv")
print("Dataset loaded")

# Perform inferences in batch
print("Performing predictions in batch ....")
y_predictions = model.predict(X_test)
print("Predictions in batch done")

# Evaluate accuracy in batch predictions
accuracy_percentage = compute_accuracy(y_pred_original.values, y_predictions)
print(f"Accuracy prediction - batch (Class): {accuracy_percentage:.2f}%")

print("Performing probabiulity predictions in batch ....")
# Perform prediction probabilities in batch and use threshold
predictions_threshold = 0.5
y_pred_proba_full = model.predict_proba(X_test)
y_pred_proba =  [round(val_1,6) for _, val_1 in y_pred_proba_full ]
y_pred = [0 if val < predictions_threshold else  1 for val in y_pred_proba ]
print("Probability predictions in batch done")

accuracy_percentage = compute_accuracy(y_pred_original.values, y_pred)
print(f"Accuracy prediction (Class): {accuracy_percentage:.2f}%")  # Output: Accuracy: 80.00%
accuracy_percentage = compute_accuracy(y_pred_proba_original.values, y_pred_proba)
print(f"Accuracy prediction (proba): {accuracy_percentage:.2f}%")  # Output: Accuracy: 80.00%

# On single sample
print("Predicions in single samples...")
success = True
start = datetime.now()
for i in range(X_test.values.shape[0]):
    sample = X_test.iloc[i].values.reshape(1, -1)
    single_proba = model.predict_proba(sample)[:, 1][0]
    y_pred_single_proba = round(single_proba,6)
    # Test values in single inferences
    if  not np.isclose(y_pred_single_proba, y_pred_proba_original.values[i], atol=0.0000001):
        print(f"sample {i} not OK")
        success = False
end = datetime.now()
delta = end - start
print(f"Done in: {delta}")
if success:
    print("Single samples predictions are correct!")

# CREATE SINGLE DATAFRAME
# BOXCOUNTERS FOR INFERENCE:
idx = 10
sample_single = X_test.iloc[idx].values.reshape(1, -1)[0]
# BOX
obssTime_box = sample_single[0]
rxTime_box = sample_single[1]
txTime_box = sample_single[2]
tx_Mbps_box = sample_single[3]
tx_Mbps_lag_1_box = sample_single[9]
tx_Mbps_lag_2_box = sample_single[11]
tx_Mbps_lag_3_box = sample_single[13]
tx_Mbps_avg_3_box = sample_single[15]
tx_Mbps_avg_5_box = sample_single[17]
tx_Mbps_avg_7_box = sample_single[19]
rx_Mbps_box = sample_single[4]
rx_Mbps_lag_1_box = sample_single[10]
rx_Mbps_lag_2_box = sample_single[12]
rx_Mbps_lag_3_box = sample_single[14]
rx_Mbps_avg_3_box = sample_single[16]
rx_Mbps_avg_5_box = sample_single[18]
rx_Mbps_avg_7_box = sample_single[20]
tx_err_pps_box = sample_single[5]
tx_ber_box = sample_single[6]
rx_pps_box = sample_single[7]
tx_pps_box = sample_single[8]

# STATION
signalStrength = sample_single[21]
signalStrength_lag1 = sample_single[34]
signalStrength_lag2 = sample_single[37]
signalStrength_lag3 = sample_single[40]
signalStrength_lag5 = sample_single[43]
signalStrength_lag7 = sample_single[46]
signalStrength_avg3 = sample_single[49]
signalStrength_avg5 = sample_single[52]
signalStrength_avg7 = sample_single[55]
signalStrength_avg10 = sample_single[58]
tx_Mbps = sample_single[26]
tx_Mbps_lag1 = sample_single[32]
tx_Mbps_lag2 = sample_single[35]
tx_Mbps_lag3 = sample_single[38]
tx_Mbps_lag5 = sample_single[41]
tx_Mbps_lag7 = sample_single[44]
tx_Mbps_avg3 = sample_single[47]
tx_Mbps_avg5 = sample_single[50]
tx_Mbps_avg7 = sample_single[53]
tx_Mbps_avg10 = sample_single[56]
rx_Mbps = sample_single[27]
rx_Mbps_lag1 = sample_single[33]
rx_Mbps_lag2 = sample_single[36]
rx_Mbps_lag3 = sample_single[39]
rx_Mbps_lag5 = sample_single[42]
rx_Mbps_lag7 = sample_single[45]
rx_Mbps_avg3 = sample_single[48]
rx_Mbps_avg5 = sample_single[51]
rx_Mbps_avg7 = sample_single[54]
rx_Mbps_avg10 = sample_single[57]
downlinkMCS = sample_single[22]
inactive = sample_single[23]
uplinkMCS = sample_single[24]
uplinkShortGuard = sample_single[25]
rx_pps = sample_single[28]
tx_pps = sample_single[29]
tx_err_pps = sample_single[30]
tx_ber = sample_single[31]


# Create dataframe
data = [
    obssTime_box,
    rxTime_box,
    txTime_box,
    tx_Mbps_box,
    rx_Mbps_box,
    tx_err_pps_box,
    tx_ber_box,
    rx_pps_box,
    tx_pps_box,
    tx_Mbps_lag_1_box,
    rx_Mbps_lag_1_box,
    tx_Mbps_lag_2_box,
    rx_Mbps_lag_2_box,
    tx_Mbps_lag_3_box,
    rx_Mbps_lag_3_box,
    tx_Mbps_avg_3_box,
    rx_Mbps_avg_3_box,
    tx_Mbps_avg_5_box,
    rx_Mbps_avg_5_box,
    tx_Mbps_avg_7_box,
    rx_Mbps_avg_7_box,
    signalStrength,
    downlinkMCS,
    inactive,
    uplinkMCS,
    uplinkShortGuard,
    tx_Mbps,
    rx_Mbps,
    rx_pps,
    tx_pps,
    tx_err_pps,
    tx_ber,
    tx_Mbps_lag1,
    rx_Mbps_lag1,
    signalStrength_lag1,
    tx_Mbps_lag2,
    rx_Mbps_lag2,
    signalStrength_lag2,
    tx_Mbps_lag3,
    rx_Mbps_lag3,
    signalStrength_lag3,
    tx_Mbps_lag5,
    rx_Mbps_lag5,
    signalStrength_lag5,
    tx_Mbps_lag7,
    rx_Mbps_lag7,
    signalStrength_lag7,
    tx_Mbps_avg3,
    rx_Mbps_avg3,
    signalStrength_avg3,
    tx_Mbps_avg5,
    rx_Mbps_avg5,
    signalStrength_avg5,
    tx_Mbps_avg7,
    rx_Mbps_avg7,
    signalStrength_avg7,
    tx_Mbps_avg10,
    rx_Mbps_avg10,
    signalStrength_avg10,
]

# Check if arrays are similar
for j in range(len(data)):
    if sample_single[j] != data[j]:
        print("ERROR: Dataframe created is different from original")

# Create dataframe object
data_values = np.array([data])

# Perform inference on created df
y_pred_single_df = model.predict(data_values)
y_pred_single_proba_df = model.predict_proba(data_values)[:, 1]

# Compare result
if np.isclose(y_pred_single_df[0], y_pred_original.values[idx][0], atol=0.0000001) and np.isclose(y_pred_single_proba_df[0], y_pred_proba_original.values[idx][0], atol=0.0000001):
    print("Single prediction in created dataframe OK")
else:
    print("ERROR: Wrong result in single prediction dataframe")
