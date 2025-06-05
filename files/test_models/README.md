# Models tests
This file explains how to use the test_model.py script in order to test the trained models.

Each model located in files/models contains the following structure:

[MODEL].pkl           -> Model file
X_test.csv            -> Test input data
y_pred.csv            -> Test output predictions (used to compare to results)
y_pred_proba.csv      -> Test output probabilities (used to compare to results)

The model can be tested in batch inferences or single inferences

Create venv and install requirements
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run batch test
Inferences are made on a batch of all the X_test lines

```bash
python3 files/test_models/test_model.py MLP_12_3 files/models batch
```

## Run one by one inferences test
Inferences are made on a batch of all the X_test lines

```bash
python3 files/test_models/test_model.py MLP_12_3 files/models single
```

## Run one inference creating a dataframe test
Inferences are made on a batch of all the X_test lines

```bash
python3 files/test_models/test_model.py MLP_12_3 files/models single-dataframe
```
