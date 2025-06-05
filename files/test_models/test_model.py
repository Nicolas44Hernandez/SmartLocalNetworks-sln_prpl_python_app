import joblib
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

pd.options.display.float_format = '{:.4f}'.format # Float display format

def load_model(model_file: str):
    """Load model"""
    print("---------------------------------------------------------------------------------------------------------------")
    print(f"                                 Loading model {model_file}")
    print("---------------------------------------------------------------------------------------------------------------")

    # Load model
    model = joblib.load(model_file)
    print("Model loaded")
    return model

def load_data(model_dir: str):
    """Load test data"""
    print("Loading dataset ....")
    x_test = pd.read_csv(f"{model_dir}/X_test.csv")
    # Load the original lists to evaluate predictions
    y_pred_proba_original = pd.read_csv(f"{model_dir}/y_pred_proba.csv")
    y_pred_original = pd.read_csv(f"{model_dir}/y_pred.csv")
    print("Test data loaded")

    return x_test, y_pred_proba_original, y_pred_original

def compute_accuracy(list1, list2):
    # Ensure both lists are of the same length
    if len(list1) != len(list2):
        raise ValueError("Lists must be of the same length to compute accuracy.")

    # Count matching elements
    matches = sum(1 for a, b in zip(list1, list2) if a == b)

    # Calculate accuracy percentage
    accuracy = (matches / len(list1)) * 100
    return accuracy

def perform_inferences_in_batch(model, x_test, y_pred_original, y_pred_proba_original):
    """Perform inferences in batch"""

    print("\n\nPerforming predictions in batch ....")
    y_predictions = model.predict(x_test)
    print("Predictions in batch done")

    # Evaluate accuracy in batch predictions
    accuracy_percentage = compute_accuracy(y_pred_original.values, y_predictions)
    print(f"Accuracy prediction - batch (Class): {accuracy_percentage:.2f}%")

    print("\n\nPerforming probabiulity predictions in batch ....")
    # Perform prediction probabilities in batch and use threshold
    predictions_threshold = 0.5
    y_pred_proba_full = model.predict_proba(x_test)
    y_pred_proba =  [round(val_1,6) for _, val_1 in y_pred_proba_full ]
    y_pred = [0 if val < predictions_threshold else  1 for val in y_pred_proba ]
    print("\nProbability predictions in batch done")

    accuracy_percentage = compute_accuracy(y_pred_original.values, y_pred)
    print(f"Accuracy prediction - bach ussing threshold (Class): {accuracy_percentage:.2f}%")  # Output: Accuracy: 80.00%
    accuracy_percentage = compute_accuracy(y_pred_proba_original.values, y_pred_proba)
    print(f"Accuracy prediction (proba): {accuracy_percentage:.2f}%")  # Output: Accuracy: 80.00%

def perform_predictions_in_single_samples(model, x_test, y_pred_proba_original):
    """Perform predictions one by one"""
    # On single sample
    print("Predicions in single samples...")
    success = True
    start = datetime.now()
    for i in range(x_test.values.shape[0]):
        sample = x_test.iloc[i].values.reshape(1, -1)
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


def main():

    # Load args
    parser = argparse.ArgumentParser(description='Model args')
    parser.add_argument('model_name', type=str, help='Model name [MLP_12_3, MLP_XP4_16_16_16]', default="MLP_12_3")
    parser.add_argument('model_dir', type=str, help='Model dir', default="files/models/")
    parser.add_argument('mode', type=str, help='Test mode [batch, single]', default="batch")
    args = parser.parse_args()

    model_name = args.model_name
    model_dir = args.model_dir
    model_dir = f"{model_dir}/{model_name}"
    mode = args.mode

    # Load model
    model_file = f"{model_dir}/{model_name}_OPTIM.pkl"
    model = load_model(model_file)

    # Load test data
    x_test, y_pred_proba_original, y_pred_original = load_data(model_dir)

    if mode == "batch":
        # perform predictions in batch
        perform_inferences_in_batch(model, x_test, y_pred_original, y_pred_proba_original)

    if mode == "single":
        # perform predictions one by one
        perform_predictions_in_single_samples(model, x_test, y_pred_proba_original)

if __name__ == "__main__":
    main()
