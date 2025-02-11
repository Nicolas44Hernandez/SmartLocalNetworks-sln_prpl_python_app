"""Wifi Bands manager"""

import os
import logging
import threading
import queue
from datetime import datetime
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.interfaces.mlp_interface import MlpModelInterface
from server.common import samples_queue
from server.managers.mlp_inference_manager import mlp_inference_manager_service
from .counters import Counters
from .common import COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE

logger = logging.getLogger(__name__)


class WifiBandsManager(threading.Thread, Counters):
    """Manager for wifi control"""

    amx_usp_interface: AmxUspInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the WifiBandsManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()

            # Initialize MLP model interface
            self.mlp_model_interface = MlpModelInterface(model_path=app.config["MODEL"])

            # Initialize counters
            self.purge_counters_timer_in_secs = app.config["COUNTERS"]["PURGE_TIMER_IN_SECS"]
            self.init_counters()

            # Run CountWifi bands inferences in dedicated thread
            super(WifiBandsManager, self).__init__(name="WifiBandsInferencesThread")
            self.setDaemon(True)
            logger.info("Running wifi bands manager inferences loop in dedicated thread")
            self.start()

    def run(self):
        """Run thread"""
        while True:
            try:
                sample = samples_queue.get(timeout=0.3)
            except queue.Empty:
                sample = None
            if sample is not None:  # Counters sample waitting in queue
                try:
                    sample_5GHz = sample["box_counters"]["5GHz"]
                    sample_2GHz = sample["box_counters"]["2.4GHz"]
                    sample_stations = sample["stations_counters"]
                except:
                    logger.error("Error unpacking sample")
                    self.init_counters()
                    continue
                # Update box counters
                if not self.update_box_counter(band="5GHz", sample=sample_5GHz):
                    logger.error("Error in box counters update for 5GHz, counters are reset")
                    self.init_counters()
                    continue
                if not self.update_box_counter(band="2.4GHz", sample=sample_2GHz):
                    logger.error("Error in box counters update for 2.4GHz, counters are reset")
                    self.init_counters()
                    continue
                # Update stations counters
                if not self.update_stations_counters(sample=sample_stations):
                    logger.error("Error in stations counters update, counters are reset")
                    self.init_counters()
                    continue

                # Purge disconnected stations from counters
                if not self.purge_stations_counters():
                    logger.error("Error in stations counters purge, counters are reset")
                    self.init_counters()
                    continue

                # Perform inferences
                ret, inference_results = mlp_inference_manager_service.perform_inferences(
                    counters_2GHz=self.counters_2GHz,
                    counters_5GHz=self.counters_5GHz,
                    counters_stations=self.counters_stations,
                    counters_array_min_size=COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE,
                )
                if not ret:
                    logger.error("Error when performing inferences, counters are reset")
                    self.init_counters()
                    continue

                # Append results to stations counters
                self.append_inference_results_to_counters(inference_results=inference_results)

                # TODO: post to web server

                # Print counters for debug
                self.print_counters()

                # Evaluate band status change
                self.update_band_status_if_necessary()

    def update_band_status_if_necessary(self):
        """Evaluate band status and switch if necessary"""
        now = datetime.now()
        if os.getenv("FLASK_ENV") != "DEVELOPMENT":
            current_band_status = self.get_band_status()
        else:
            current_band_status = "Down"

        # Filter valid inferences
        inferences = mlp_inference_manager_service.get_valid_inferences(
            counters_stations=self.counters_stations
        )
        if len(inferences) == 0:
            return

        # If the 5 GHz band is ON:
        # If for all the stations the inference result is OFF -> then turn OFF the band
        # Else keep the band ON
        if current_band_status == "Up":
            for prediction in inferences:
                if prediction.prediction:
                    logger.error(f"Station {prediction.station} inference requires the band ON, the 5GHz band remains ON")
                    return
            logger.error(f"Setting 5GHz band OFF")
            self.set_band_status(new_status=False)
            return

        # If the 5 GHz band is OFF:
        # If for at least one stations the inference result is ON -> then turn ON the band
        # Else keep the band OFF
        else:
            for prediction in inferences:
                if prediction.prediction:
                    logger.error(f"Station {prediction.station} inference requires the band ON")
                    logger.error(f"Setting 5GHz band ON")
                    self.set_band_status(new_status=True)
                    return
            logger.error(f"5GHz band will remain OFF")
            return

    def get_band_status(self):
        """Execute get wifi band status command in the livebox using AMX USP """
        cmd = "Device.WiFi.Radio.2.Status"
        logger.debug(f"Getting wifi status - {cmd}")
        status = self.amx_usp_interface.read_object(path=cmd)[0]['Device.WiFi.Radio.2.']['Status']
        logger.debug(f"status: {status}")
        return status

    def set_band_status(self, new_status: bool):
        """Execute set wifi band status command in the livebox using AMX USP"""
        # Restart counters only if setting band ON
        if new_status:
            self.init_counters()

        # Retrieve path and params
        path = "Device.WiFi.Radio.2"
        params = {"Enable": "1"} if new_status else {"Enable": "0"}
        logger.info(f"Setting wifi 5GHz band status to {new_status}")
        ret = self.amx_usp_interface.set_object(path=path, params=params)
        logger.info(f"Response: {ret}")
        return


wifi_5GHz_band_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
