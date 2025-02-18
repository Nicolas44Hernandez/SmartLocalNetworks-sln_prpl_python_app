import joblib
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

pd.options.display.float_format = '{:.4f}'.format # Float display format

# Constants :
target_names = ['class 0 - 5Ghz - OFF', 'class 1 - 5Ghz - ON ']

parser = argparse.ArgumentParser(description='Model args')
parser.add_argument('model_name', type=str, help='Model name [MLP_C, XGBoost_C, LGBM_C]')
parser.add_argument('model_dir', type=str, help='Model dir', default="models/")
args = parser.parse_args()

model_name = args.model_name
dir = args.model_dir
models_dir = f"{dir}/{model_name}"

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
start = datetime.now()
y_pred = model_pipeline.predict(X_train.values)
test_pred = model_pipeline.predict_proba(X_train.values)[:, 1]
end = datetime.now()
delta = end - start
print(f"Done in: {delta}")

# On single sample
print("Predicions in single sample...")
success = True
start = datetime.now()
for i in range(X_train.values.shape[0]):
    sample = X_train.iloc[i].values.reshape(1, -1)
    y_pred_single = model_pipeline.predict(sample)
    test_pred_single = model_pipeline.predict_proba(sample)[:, 1]
    # Test values in single inferences
    if  not np.isclose(y_pred_single[0], y_pred[i], atol=0.0000001) or not np.isclose(test_pred_single[0], test_pred[i], atol=0.0000001):
        print(f"sample {i} not OK")
        success = False
end = datetime.now()
delta = end - start
print(f"Done in: {delta}")
if success:
    print("Single samples are correct!")


# BOXCOUNTERS FOR INFERENCE:
rx_Mbps_box_array=[0.0001, 0.0002, 0.0002, 0.0, 0.0001, 0.0001, 0.0, 0.0, 0.0, 0.0003]
tx_Mbps_box_array=[0.00030000000000000003, 0.0005, 0.0007, 0.0, 0.00030000000000000003, 0.038599999999999995, 0.0002, 0.0, 0.0002, 0.0003]
noise=[-88, -85, -86, -86, -86, -87, -86, -86, -85, -86]
rx_pps_box=0.0
tx_pps_box=0.0
load_box=31.0
freeTime=69.0
rxTime=0.0
txTime=6.5
obssTime=12
intTime=26
vendorStats_glitch=2514
noise_air=-86
tx_err_ps=0.0
tx_ber=0.0

# Compute BOX values
rx_Mbps_box = rx_Mbps_box_array[-1]
rx_Mbps_lag1_box = rx_Mbps_box_array[-2]
rx_Mbps_lag2_box = rx_Mbps_box_array[-3]
rx_Mbps_lag3_box = rx_Mbps_box_array[-4]
rx_Mbps_avg3_box = np.mean(rx_Mbps_box_array[-3:])
rx_Mbps_avg5_box = np.mean(rx_Mbps_box_array[-5:])
rx_Mbps_avg7_box = np.mean(rx_Mbps_box_array[-7:])
tx_Mbps_box = tx_Mbps_box_array[-1]
tx_Mbps_lag1_box = tx_Mbps_box_array[-2]
tx_Mbps_lag2_box = tx_Mbps_box_array[-3]
tx_Mbps_lag3_box = tx_Mbps_box_array[-4]
tx_Mbps_avg3_box = np.mean(tx_Mbps_box_array[-3:])
tx_Mbps_avg5_box = np.mean(tx_Mbps_box_array[-5:])
tx_Mbps_avg7_box = np.mean(tx_Mbps_box_array[-7:])
noise_box = noise[-1]
noise_lag3_box = noise[-4]
noise_avg3_box = np.mean(noise[-3:])
noise_avg5_box = np.mean(noise[-5:])
noise_avg7_box = np.mean(noise[-7:])

# STATION COUNTERS:
tx_Mbps_station_array=[0.0231, 0.0003, 0.0006, 0.0004, 0.0, 0.0003, 0.0192, 0.0001, 0.0, 0.0001]
rx_Mbps_station_array=[0.007, 0.0005, 0.0005, 0.0005, 0.0001, 0.0004, 0.0004, 0.0, 0.0, 0.0]
signalStrength_st=[-34, -33, -33, -41, -40, -36, -33, -33, -33, -33]
rx_pps=0.0
tx_pps=0.19998384130562252
uplinkMCS=0
lastDataUplinkRate=6000
lastDataDownlinkRate=816700
uplinkShortGuard=0
downlinkMCS=8
avgSignalStrengthByChain=-36
signalNoiseRatio=0

# Compute STATION values
rx_Mbps = rx_Mbps_station_array[-1]
rx_Mbps_lag1 = rx_Mbps_station_array[-2]
rx_Mbps_lag2 = rx_Mbps_station_array[-3]
rx_Mbps_lag3 = rx_Mbps_station_array[-4]
rx_Mbps_lag5 = rx_Mbps_station_array[-6]
rx_Mbps_lag7 = rx_Mbps_station_array[-8]
rx_Mbps_avg3 = np.mean(rx_Mbps_station_array[-3:])
rx_Mbps_avg5 = np.mean(rx_Mbps_station_array[-5:])
rx_Mbps_avg7 = np.mean(rx_Mbps_station_array[-7:])
rx_Mbps_avg10 = np.mean(rx_Mbps_station_array)
tx_Mbps = tx_Mbps_station_array[-1]
tx_Mbps_lag1 = tx_Mbps_station_array[-2]
tx_Mbps_avg3 = np.mean(tx_Mbps_station_array[-3:])
tx_Mbps_avg5 = np.mean(tx_Mbps_station_array[-5:])
signalStrength = signalStrength_st[-1]
signalStrength_lag1 = signalStrength_st[-2]
signalStrength_lag2 = signalStrength_st[-3]
signalStrength_lag3 = signalStrength_st[-4]
signalStrength_lag5 = signalStrength_st[-6]
signalStrength_lag7 = signalStrength_st[-8]
signalStrength_avg3 = np.mean(signalStrength_st[-3:])
signalStrength_avg5 = np.mean(signalStrength_st[-5:])
signalStrength_avg7 = np.mean(signalStrength_st[-7:])
signalStrength_avg10 = np.mean(signalStrength_st[-10:])

# Dataframe for test
#rx_Mbps_box, rx_Mbps_avg3_box, load_box, freeTime, rx_Mbps_avg5_box, rx_Mbps_avg7_box, rx_Mbps_lag1_box, tx_Mbps_avg7_box, rxTime, rx_Mbps_lag1_box, rx_Mbps_avg5_box, tx_pps_box, tx_Mbps_avg3_box, rx_Mbps_lag3_box, rx_pps_box, tx_Mbps_lag1_box, tx_Mbps_lag2_box, tx_Mbps_box, tx_Mbps_lag3_box, lastDataUplinkRate, uplinkMCS, lastDataDownlinkRate, rx_Mbps, vendorStats_glitch, rx_pps, obssTime, signalStrength_avg10, signalStrength_avg7, txTime, signalStrength_avg5, signalStrength_avg3, signalStrength_lag1, uplinkShortGuard, signalStrength_lag5, tx_Mbps, signalStrength_lag2, signalStrength_lag3, downlinkMCS, tx_ber, rx_Mbps_avg3, rx_Mbps_lag1, signalStrength, signalStrength_lag7, rx_Mbps_avg5, rx_Mbps_avg7, intTime, tx_Mbps_avg3, tx_pps, avgSignalStrengthByChain, noise_avg7_box, rx_Mbps_lag2, noise_avg5_box, rx_Mbps_avg10, signalNoiseRatio, rx_Mbps_lag7, tx_Mbps_avg5, tx_Mbps_lag1, noise_lag3_box, noise_avg3_box, tx_err_ps, noise_box, rx_Mbps_lag3, noise_air, rx_Mbps_lag5 = data_sample_test


# Dataframe from sample
# data_sample_test = sample[0].tolist()
# rx_Mbps_box, rx_Mbps_avg3_box, load_box, freeTime, rx_Mbps_avg5_box, rx_Mbps_avg7_box, rx_Mbps_lag1_box, tx_Mbps_avg7_box, rxTime, rx_Mbps_lag2_box, tx_Mbps_avg5_box, tx_pps_box, tx_Mbps_avg3_box, rx_Mbps_lag3_box, rx_pps_box, tx_Mbps_lag1_box, tx_Mbps_lag2_box, tx_Mbps_box, tx_Mbps_lag3_box, lastDataUplinkRate, uplinkMCS, lastDataDownlinkRate, rx_Mbps, vendorStats_glitch, rx_pps, obssTime, signalStrength_avg10, signalStrength_avg7, txTime, signalStrength_avg5, signalStrength_avg3, signalStrength_lag1, uplinkShortGuard, signalStrength_lag5, tx_Mbps, signalStrength_lag2, signalStrength_lag3, downlinkMCS, tx_ber, rx_Mbps_avg3, rx_Mbps_lag1, signalStrength, signalStrength_lag7, rx_Mbps_avg5, rx_Mbps_avg7, intTime, tx_Mbps_avg3, tx_pps, avgSignalStrengthByChain, noise_avg7_box, rx_Mbps_lag2, noise_avg5_box, rx_Mbps_avg10, signalNoiseRatio, rx_Mbps_lag7, tx_Mbps_avg5, tx_Mbps_lag1, noise_lag3_box, noise_avg3_box, tx_err_ps, noise_box, rx_Mbps_lag3, noise_air, rx_Mbps_lag5 = data_sample_test

# Create dataframe
data = [
    rx_Mbps_box,
    rx_Mbps_avg3_box,
    load_box,
    freeTime,
    rx_Mbps_avg5_box,
    rx_Mbps_avg7_box,
    rx_Mbps_lag1_box,
    tx_Mbps_avg7_box,
    rxTime,
    rx_Mbps_lag2_box,
    tx_Mbps_avg5_box,
    tx_pps_box,
    tx_Mbps_avg3_box,
    rx_Mbps_lag3_box,
    rx_pps_box,
    tx_Mbps_lag1_box,
    tx_Mbps_lag2_box,
    tx_Mbps_box,
    tx_Mbps_lag3_box,
    lastDataUplinkRate,
    uplinkMCS,
    lastDataDownlinkRate,
    rx_Mbps,
    vendorStats_glitch,
    rx_pps,
    obssTime,
    signalStrength_avg10,
    signalStrength_avg7,
    txTime,
    signalStrength_avg5,
    signalStrength_avg3,
    signalStrength_lag1,
    uplinkShortGuard,
    signalStrength_lag5,
    tx_Mbps,
    signalStrength_lag2,
    signalStrength_lag3,
    downlinkMCS,
    tx_ber,
    rx_Mbps_avg3,
    rx_Mbps_lag1,
    signalStrength,
    signalStrength_lag7,
    rx_Mbps_avg5,
    rx_Mbps_avg7,
    intTime,
    tx_Mbps_avg3,
    tx_pps,
    avgSignalStrengthByChain,
    noise_avg7_box,
    rx_Mbps_lag2,
    noise_avg5_box,
    rx_Mbps_avg10,
    signalNoiseRatio,
    rx_Mbps_lag7,
    tx_Mbps_avg5,
    tx_Mbps_lag1,
    noise_lag3_box,
    noise_avg3_box,
    tx_err_ps,
    noise_box,
    rx_Mbps_lag3,
    noise_air,
    rx_Mbps_lag5,
]
print(data)
# # Check if arrays are similar
# for j in range(len(data_sample_test)):
#     if data_sample_test[j] != data[j]:
#         print("different!!")


data_values = np.array([data])


# Perform inference
y_pred_single_df = model_pipeline.predict(data_values)
test_pred_single_df = model_pipeline.predict_proba(data_values)[:, 1]

a = 4




# Write CLASSIFICATION Results on Train DATASET in csv file
print("Writting results in files [y_pred_train_dataset.csv, test_pred_train_dataset.csv]")
np.savetxt('y_pred_train_dataset.csv', y_pred, delimiter=',', fmt='%d')
np.savetxt('test_pred_train_dataset.csv', test_pred, delimiter=',', fmt='%f')
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
