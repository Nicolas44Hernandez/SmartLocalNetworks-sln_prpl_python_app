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

    def __init__(self, model_path: str):
        logger.info("initializing the MlpModel")

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
            data.append(
                [
                    box_data.rx_Mbps,
                    box_data.rx_Mbps_avg3,
                    box_data.load,
                    box_data.freeTime,
                    box_data.rx_Mbps_avg5,
                    box_data.rx_Mbps_avg7,
                    box_data.rx_Mbps_lag1,
                    box_data.tx_Mbps_avg7,
                    box_data.rxTime,
                    box_data.rx_Mbps_lag1,
                    box_data.rx_Mbps_avg5,
                    box_data.tx_pps,
                    box_data.tx_Mbps_avg3,
                    box_data.rx_Mbps_lag3,
                    box_data.rx_pps,
                    box_data.tx_Mbps_lag1,
                    box_data.tx_Mbps_lag2,
                    box_data.tx_Mbps,
                    box_data.tx_Mbps_lag3,
                    station_data.lastDataUplinkRate,
                    station_data.uplinkMCS,
                    station_data.lastDataDownlinkRate,
                    station_data.rx_Mbps,
                    box_data.vendorStats_glitch,
                    station_data.rx_pps,
                    box_data.obssTime,
                    station_data.signalStrength_avg10,
                    station_data.signalStrength_avg7,
                    box_data.txTime,
                    station_data.signalStrength_avg5,
                    station_data.signalStrength_avg3,
                    station_data.signalStrength_lag1,
                    station_data.uplinkShortGuard,
                    station_data.signalStrength_lag5,
                    station_data.tx_Mbps,
                    station_data.signalStrength_lag2,
                    station_data.signalStrength_lag3,
                    station_data.downlinkMCS,
                    box_data.tx_ber,
                    station_data.rx_Mbps_avg3,
                    station_data.rx_Mbps_lag1,
                    station_data.signalStrength,
                    station_data.signalStrength_lag7,
                    station_data.rx_Mbps_avg5,
                    station_data.rx_Mbps_avg7,
                    box_data.intTime,
                    station_data.tx_Mbps_avg3,
                    station_data.tx_pps,
                    station_data.avgSignalStrengthByChain,
                    box_data.noise_avg7,
                    station_data.rx_Mbps_lag2,
                    box_data.noise_avg5,
                    station_data.rx_Mbps_avg10,
                    station_data.signalNoiseRatio,
                    station_data.rx_Mbps_lag7,
                    station_data.tx_Mbps_avg5,
                    station_data.tx_Mbps_lag1,
                    box_data.noise_lag3,
                    box_data.noise_avg3,
                    box_data.tx_err_ps,
                    box_data.noise,
                    station_data.rx_Mbps_lag3,
                    box_data.noise_air,
                    station_data.rx_Mbps_lag5,
                ]
            )

        # Convert to nd array
        data_values = np.array(data)

        # Perform inference
        try:
            prediction = self.model_pipeline.predict(data_values)
            probability = self.model_pipeline.predict_proba(data_values)[:, 1]
        except:
            logger.error("Error performing inference in batch")
            return False

        # Generate result object
        inference_results = []
        for idx, station_data in enumerate(stations_data):
            inference_results.append(
                SingleStationInferenceResult(
                    station=station_data.station,
                    prediction=bool(prediction[idx]),
                    probability=float(probability[idx]),
                )
            )

        return inference_results

