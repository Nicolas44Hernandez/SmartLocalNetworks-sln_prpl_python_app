#!/bin/bash

echo "SLN Models tests"

echo " **************** MLP Model ************************** "
python3 test_models/test_model.py MLP_C
python3 test_models/compare_results.py MLP_C

echo " **************** XGBoost Model ************************** "
python3 test_models/test_model.py XGBoost_C
python3 test_models/compare_results.py XGBoost_C

echo " **************** LGBM Model ************************** "
python3 test_models/test_model.py LGBM_C
python3 test_models/compare_results.py LGBM_C