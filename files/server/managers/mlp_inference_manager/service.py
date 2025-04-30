"""MLP inference manager"""

import logging
from typing import Iterable, Tuple
import numpy as np
from datetime import datetime, timedelta
from flask import Flask
from server.interfaces.mlp_interface import MlpModelInterface
from server.common import StationCounters, SingleStationInferenceResult, InferencesInput

logger = logging.getLogger(__name__)

class MlpInferenceManager():
    """Manager for MLP inferences"""

    mlp_model_interface: MlpModelInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the MlpInferenceManager")

            # Initialize MLP model interface
            self.mlp_model_interface = MlpModelInterface(
                model_path=app.config["MODEL"],
                predictions_threshold=app.config["PREDICTIONS_THRESHOLD"]
            )


    def perform_inferences(
            self,
            inference_input: InferencesInput,
        ) -> Tuple[bool, Iterable[SingleStationInferenceResult]]:
        """Perform inferences on counters data"""

        # If counters not filled yet
        if inference_input is None:
                return True, []

        # Perform inferences
        inference_results = self.mlp_model_interface.perform_inference(
            box_data=inference_input.box_data,
            stations_data=inference_input.stations_data,
        )
        if not inference_results:
            logger.error("Error when performing inferences")
            return False, []

        return True, inference_results

    def get_valid_inferences(self, counters_stations: Iterable[StationCounters]) -> Iterable[SingleStationInferenceResult]:
        now = datetime.now()
        valid_inferences=[]
        for station in counters_stations:
            if len(counters_stations[station].inferences_results) > 0:
                # Old counters filter
                if now - counters_stations[station].last_sample_timestamp < timedelta(seconds=2):
                    # Append inference result
                    valid_inferences.append(counters_stations[station].inferences_results[-1])
        return valid_inferences


mlp_inference_manager_service: MlpInferenceManager = MlpInferenceManager()
""" MLP manager service singleton"""
