"""MLP model interface package"""

import os
import logging
from typing import Iterable
import joblib
import pandas as pd
import numpy as np
import sklearn
import sklearn.pipeline
from server.common import ServerBoxException, ErrorCode, BoxDataForInferenceInput, StationDataForInferenceInput, SingleStationInferenceResult


pd.options.display.float_format = '{:.4f}'.format # Float display format

logger = logging.getLogger(__name__)

class MlpModel:
    """Service class for MLP model interface"""

    model_pipeline: sklearn.pipeline.Pipeline

    def __init__(self, model_path: str, predictions_threshold: float):
        logger.info("initializing the MlpModel")

        self.predictions_threshold = predictions_threshold

        # Check if model file exists
        if not os.path.exists(model_path):
            raise ServerBoxException(ErrorCode.MODEL_FILE_NOT_FOUND)

        # Load model
        logger.info(f"Loading model: {model_path}")
        self.model_pipeline = joblib.load(model_path)
        logging.info("Model loaded")

    def perform_inference(
            self,
            box_data: BoxDataForInferenceInput,
            stations_data: Iterable[StationDataForInferenceInput],
    ) -> Iterable[SingleStationInferenceResult]:
        """Create a batch and perform inference to predict to a list of stations"""
        # Extract data to list of lists
        data = []
        for station_data in stations_data:

            ################PRINT FOR TEST#####################

            logger.debug(
                f"INFERENCE FOR STATION {station_data.station}:  "
                f"box_data.obssTime : {box_data.obssTime}  "
                f"box_data.rxTime : {box_data.rxTime}  "
                f"box_data.txTime : {box_data.txTime}  "
                f"box_data.tx_Mbps : {box_data.tx_Mbps}  "
                f"box_data.rx_Mbps : {box_data.rx_Mbps}  "
                f"box_data.rx_pps : {box_data.rx_pps}  "
                f"box_data.tx_pps : {box_data.tx_pps}  "
                f"station_data.signalStrength : {station_data.signalStrength}  "
                f"station_data.downlinkMCS : {station_data.downlinkMCS}  "
                f"station_data.uplinkMCS : {station_data.uplinkMCS}  "
                f"station_data.uplinkShortGuard : {station_data.uplinkShortGuard}  "
                f"station_data.tx_Mbps : {station_data.tx_Mbps}  "
                f"station_data.rx_Mbps : {station_data.rx_Mbps}  "
                f"station_data.rx_pps : {station_data.rx_pps}  "
                f"station_data.tx_pps : {station_data.tx_pps}  "
                f"station_data.tx_err_pps : {station_data.tx_err_pps}  "
            )
            ##################################################
            data.append(
                [
                    box_data.obssTime,
                    box_data.rxTime,
                    box_data.txTime,
                    box_data.tx_Mbps,
                    box_data.rx_Mbps,
                    box_data.rx_pps,
                    box_data.tx_pps,
                    station_data.signalStrength,
                    station_data.downlinkMCS,
                    station_data.uplinkMCS,
                    station_data.uplinkShortGuard,
                    station_data.tx_Mbps,
                    station_data.rx_Mbps,
                    station_data.rx_pps,
                    station_data.tx_pps,
                    station_data.tx_err_pps,
                ]
            )

        # Convert to nd array
        data_values = np.array(data)

        # Perform inference
        try:
            # Perform inference
            prediction_probabilities = self.model_pipeline.predict_proba(data_values)[:, 1]
            predictions_class = [0 if val < self.predictions_threshold else  1 for val in prediction_probabilities ]

        except Exception as e:
            logger.error("Error performing inference in batch")
            return False

        # Generate result object
        inference_results = []
        for idx, station_data in enumerate(stations_data):
            inference_results.append(
                SingleStationInferenceResult(
                    station=station_data.station,
                    status=bool(predictions_class[idx]),
                    probability=float(prediction_probabilities[idx]),
                )
            )

        return inference_results

