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

            ################PRINT FOR TEST#####################
            logger.debug(
                f"INFERENCE FOR STATION {station_data.station}:  "
                f"box_data.rx_Mbps:{box_data.rx_Mbps}  "
                f"box_data.rx_Mbps_avg3:{box_data.rx_Mbps_avg3}  "
                f"box_data.load:{box_data.load}  "
                f"box_data.freeTime:{box_data.freeTime}  "
                f"box_data.rx_Mbps_avg5:{box_data.rx_Mbps_avg5}  "
                f"box_data.rx_Mbps_avg7:{box_data.rx_Mbps_avg7}  "
                f"box_data.rx_Mbps_lag1:{box_data.rx_Mbps_lag1}  "
                f"box_data.tx_Mbps_avg7:{box_data.tx_Mbps_avg7}  "
                f"box_data.rxTime:{box_data.rxTime}  "
                f"box_data.rx_Mbps_lag2:{box_data.rx_Mbps_lag2}  "
                f"box_data.tx_Mbps_avg5:{box_data.tx_Mbps_avg5}  "
                f"box_data.tx_pps:{box_data.tx_pps}  "
                f"box_data.tx_Mbps_avg3:{box_data.tx_Mbps_avg3}  "
                f"box_data.rx_Mbps_lag3:{box_data.rx_Mbps_lag3} "
                f"box_data.rx_pps:{box_data.rx_pps}  "
                f"box_data.tx_Mbps_lag1:{box_data.tx_Mbps_lag1}  "
                f"box_data.tx_Mbps_lag2:{box_data.tx_Mbps_lag2}  "
                f"box_data.tx_Mbps:{box_data.tx_Mbps}  "
                f"box_data.tx_Mbps_lag3:{box_data.tx_Mbps_lag3}  "
                f"station_data.lastDataUplinkRate:{station_data.lastDataUplinkRate}  "
                f"station_data.uplinkMCS:{station_data.uplinkMCS}  "
                f"station_data.lastDataDownlinkRate:{station_data.lastDataDownlinkRate}  "
                f"station_data.rx_Mbps:{station_data.rx_Mbps}  "
                f"box_data.vendorStats_glitch:{box_data.vendorStats_glitch}  "
                f"station_data.rx_pps:{station_data.rx_pps}  "
                f"box_data.obssTime:{box_data.obssTime}  "
                f"station_data.signalStrength_avg10:{station_data.signalStrength_avg10}  "
                f"station_data.signalStrength_avg7:{station_data.signalStrength_avg7}  "
                f"box_data.txTime:{box_data.txTime}  "
                f"station_data.signalStrength_avg5:{station_data.signalStrength_avg5}  "
                f"station_data.signalStrength_avg3:{station_data.signalStrength_avg3}  "
                f"station_data.signalStrength_lag1:{station_data.signalStrength_lag1}  "
                f"station_data.uplinkShortGuard:{station_data.uplinkShortGuard}  "
                f"station_data.signalStrength_lag5:{station_data.signalStrength_lag5}  "
                f"station_data.tx_Mbps:{station_data.tx_Mbps}  "
                f"station_data.signalStrength_lag2:{station_data.signalStrength_lag2}  "
                f"station_data.signalStrength_lag3:{station_data.signalStrength_lag3}  "
                f"station_data.downlinkMCS:{station_data.downlinkMCS}  "
                f"box_data.tx_ber:{box_data.tx_ber}  "
                f"station_data.rx_Mbps_avg3:{station_data.rx_Mbps_avg3}  "
                f"station_data.rx_Mbps_lag1:{station_data.rx_Mbps_lag1}  "
                f"station_data.signalStrength:{station_data.signalStrength}  "
                f"station_data.signalStrength_lag7:{station_data.signalStrength_lag7}  "
                f"station_data.rx_Mbps_avg5:{station_data.rx_Mbps_avg5}  "
                f"station_data.rx_Mbps_avg7:{station_data.rx_Mbps_avg7} "
                f"box_data.intTime:{box_data.intTime}  "
                f"station_data.tx_Mbps_avg3:{station_data.tx_Mbps_avg3}  "
                f"station_data.tx_pps:{station_data.tx_pps}  "
                f"station_data.avgSignalStrengthByChain:{station_data.avgSignalStrengthByChain}  "
                f"box_data.noise_avg7:{box_data.noise_avg7}  "
                f"station_data.rx_Mbps_lag2:{station_data.rx_Mbps_lag2}  "
                f"box_data.noise_avg5:{box_data.noise_avg5}  "
                f"station_data.rx_Mbps_avg10:{station_data.rx_Mbps_avg10}  "
                f"station_data.signalNoiseRatio:{station_data.signalNoiseRatio}  "
                f"station_data.rx_Mbps_lag7:{station_data.rx_Mbps_lag7}  "
                f"station_data.tx_Mbps_avg5:{station_data.tx_Mbps_avg5}  "
                f"station_data.tx_Mbps_lag1:{station_data.tx_Mbps_lag1}  "
                f"box_data.noise_lag3:{box_data.noise_lag3}  "
                f"box_data.noise_avg3:{box_data.noise_avg3} "
                f"box_data.tx_err_ps:{box_data.tx_err_ps}  "
                f"box_data.noise:{box_data.noise}  "
                f"station_data.rx_Mbps_lag3:{station_data.rx_Mbps_lag3} "
                f"box_data.noise_air:{box_data.noise_air}  "
                f"station_data.rx_Mbps_lag5:{station_data.rx_Mbps_lag5}"
            )
            ##################################################
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
                    box_data.rx_Mbps_lag2, # rx_Mbps_lag2-2g
                    box_data.tx_Mbps_avg5, #tx_Mbps_avg5-2g
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

