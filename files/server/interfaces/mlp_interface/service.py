"""MLP model interface package"""

import os
import logging
import joblib
import pandas as pd
import numpy as np
import sklearn
import sklearn.pipeline
from server.common import ServerBoxException, ErrorCode

pd.options.display.float_format = '{:.4f}'.format # Float display format

logger = logging.getLogger(__name__)

class MlpModel:
    """Service class for MLP model interface"""

    model_pipeline: sklearn.pipeline.Pipeline

    def __init__(self, model_path: str):
        logger.info("initializing the MlpModel")

        # Check if model file exists
        if not os.path.exists(model_path):
            raise ServerBoxException(ErrorCode.MODEL_FILE_NOT_FOUND)

        # Load model
        logger.info(f"Loading model: {model_path}")
        self.model_pipeline = joblib.load(model_path)
        logging.info("Model loaded")

