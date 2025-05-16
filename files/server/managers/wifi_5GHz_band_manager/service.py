"""Wifi Bands manager"""

import os
import logging
import threading
import queue
from datetime import datetime, timedelta
from typing import Iterable, Tuple
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import samples_queue, BoxDataForInferenceInput, StationDataForInferenceInput, InferencesInput
from server.managers.mlp_inference_manager import mlp_inference_manager_service
from server.notification import notification_service
from .counters import Counters
from .common import COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE

logger = logging.getLogger(__name__)


class WifiBandsManager(threading.Thread, Counters):
    """Manager for wifi control"""

    amx_usp_interface: AmxUspInterface
    dont_update_band_status_until: datetime
    band_uptime_in_minutes: int


    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the WifiBandsManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()
            self.dont_update_band_status_until = datetime.now()

            # Initialize counters
            self.purge_counters_timer_in_secs = app.config["COUNTERS"]["PURGE_TIMER_IN_SECS"]
            self.band_uptime_in_minutes = app.config["COUNTERS"]["BAND_UPTIME_IN_MINS"]
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
                    logger.error("At least one station switch band, inferences not performed")
                    continue

                # Purge disconnected stations from counters
                if not self.purge_stations_counters():
                    logger.error("Error in stations counters purge, counters are reset")
                    self.init_counters()
                    continue

                # Get inference inputs
                ret, inference_input = self.get_inferences_input_from_counters()
                if not ret:
                    logger.error("Error when creating inference input objects from counters, counters are reset")
                    self.init_counters()
                    continue

                # Perform inferences
                ret, inferences_results = mlp_inference_manager_service.perform_inferences(
                    inference_input=inference_input,
                )
                if not ret:
                    logger.error("Error when performing inferences, counters are reset")
                    self.init_counters()
                    continue

                # Append results to stations counters
                self.append_inferences_results_to_counters(inferences_results=inferences_results)


                # Print counters for debug
                self.print_counters(print_box_counters=False, print_stations_counters=False, print_inferences_results=True)

                # Evaluate band status change
                current_band_status = True if self.update_band_status_if_necessary() == "Up" else False
                #current_band_status = True

                # Notify web server
                notification_service.notify_sample_to_web_server(
                    band_status=current_band_status,
                    box_counter_2GHz=self.counters_2GHz,
                    box_counter_5GHz=self.counters_5GHz,
                    stations_counters=self.counters_stations,
                    inferences_input=inference_input,
                    inferences_results=inferences_results,
                    timestamp=sample_2GHz.timestamp,
                )

    def get_inferences_input_from_counters(self) -> Tuple[bool, Iterable[InferencesInput]]:
        """
        Create InferencesInput object from counters to
        perform inferences
        """

        if len(self.counters_2GHz.rx_Mbps) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
            logger.debug("Counters are not filled yet")
            return True, None

        # TODO: review box counters logic
        # Station is connected to which band?
        # How to manage different cases

        # If 5GHz band is OFF, counter is None
        if self.counters_5GHz is None:
            # Use only 2.4GHz counter values
            obssTime = self.counters_2GHz.obssTime
            rxTime = self.counters_2GHz.rxTime
            txTime = self.counters_2GHz.txTime
            tx_Mbps_array = self.counters_2GHz.tx_Mbps
            rx_Mbps_array = self.counters_2GHz.rx_Mbps
            rx_pps = self.counters_2GHz.rx_pps
            tx_pps = self.counters_2GHz.tx_pps
        else:
            # Compute inference box counter values from 2.4GH and 5GHz
            # TODO: WIP
            # FACTOR = 2.5
            FACTOR = 1
            _interim_obssTime = self.counters_2GHz.obssTime + (FACTOR * self.counters_5GHz.obssTime)
            obssTime = _interim_obssTime if _interim_obssTime <= 100 else 100
            _interim_rxTime = self.counters_2GHz.rxTime + (FACTOR * self.counters_5GHz.rxTime)
            rxTime = _interim_rxTime if _interim_rxTime <= 100 else 100
            _interim_txTime = self.counters_2GHz.txTime + (FACTOR * self.counters_5GHz.txTime)
            txTime = _interim_txTime if _interim_txTime <= 100 else 100
            tx_Mbps_array = [a + b for a, b in zip(self.counters_2GHz.tx_Mbps, self.counters_5GHz.tx_Mbps)]
            rx_Mbps_array = [a + b for a, b in zip(self.counters_2GHz.rx_Mbps, self.counters_5GHz.rx_Mbps)]
            rx_pps = self.counters_2GHz.rx_pps + self.counters_5GHz.rx_pps
            tx_pps = self.counters_2GHz.tx_pps + self.counters_5GHz.tx_pps

        # MODEL VALUES CONSTRAINTS [WIP]
        obssTime = obssTime if obssTime >= 1 else 1
        rxTime = rxTime if rxTime >= 1 else 1
        txTime = txTime if txTime >= 3 else 3
        rx_pps = rx_pps if rx_pps >= 5 else 5
        tx_pps = tx_pps if tx_pps >= 5 else 5
        tx_Mbps_array = [a if a >= 0.05 else 0.05 for a in tx_Mbps_array]
        rx_Mbps_array = [a if a >= 0.05 else 0.05 for a in rx_Mbps_array]


        # Create BoxDataForInferenceInput object
        try:
            box_data_for_inference = BoxDataForInferenceInput(
                obssTime=float(obssTime),
                rxTime=float(rxTime),
                txTime=float(txTime),
                tx_Mbps=float(tx_Mbps_array[-1]),
                rx_Mbps = float(rx_Mbps_array[-1]),
                rx_pps = float(rx_pps),
                tx_pps = float(tx_pps),
            )

        except:
            logger.error("Error when retreiving box counters to perform inference")
            return False, None

        # Create StationDataForInferenceInput for each station
        stations_data_for_inference = []
        # Loop over the counters stations dict
        for station in self.counters_stations:
            # Check that counters are already filled
            if len(self.counters_stations[station].rx_Mbps) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
                continue
            # Compute station values
            try:
                # MODEL VALUES CONSTRAINTS [WIP]
                station_downlinkMCS = self.counters_stations[station].downlinkMCS if self.counters_stations[station].downlinkMCS > 3 else 3
                station_tx_Mbps = [a if a >= 0.05 else 0.05 for a in self.counters_stations[station].tx_Mbps]
                station_rx_Mbps = [a if a >= 0.05 else 0.05 for a in self.counters_stations[station].rx_Mbps]
                station_rx_pps = self.counters_stations[station].rx_pps if self.counters_stations[station].rx_pps >= 5 else 5
                station_tx_pps = self.counters_stations[station].tx_pps if self.counters_stations[station].tx_pps >= 5 else 5

                stations_data_for_inference.append(
                    StationDataForInferenceInput(
                        station=station,
                        downlinkMCS = float(station_downlinkMCS),
                        tx_Mbps = float(station_tx_Mbps[-1]),
                        rx_Mbps = float(station_rx_Mbps[-1]),
                        rx_pps = float(station_rx_pps),
                        tx_pps = float(station_tx_pps),
                        tx_err_pps = float(self.counters_stations[station].tx_err_pps),
                    )
                )
            except:
                logger.error("Error when retreiving station counters to perform inference")
                return False, None

        # If counters are not filled for at least one station
        if len(stations_data_for_inference) == 0:
            logger.debug("Counters are not yet filled for at least one station")
            return True, None

        return True, InferencesInput(box_data=box_data_for_inference, stations_data=stations_data_for_inference)

    def update_band_status_if_necessary(self) -> bool:
        """
        Evaluate band status and switch if necessary
        Return: band status
        """
        if os.getenv("FLASK_ENV") != "DEVELOPMENT":
            current_band_status = self.get_band_status()
        else:
            current_band_status = "Down"

        if datetime.now() < self.dont_update_band_status_until:
            logger.info(f"Band status wont be updated until {self.dont_update_band_status_until}")
            return current_band_status

        # Filter valid inferences
        inferences = mlp_inference_manager_service.get_valid_inferences(
            counters_stations=self.counters_stations
        )
        if len(inferences) == 0:
            return current_band_status

        # If the 5 GHz band is ON:
        # If for all the stations the inference result is OFF -> then turn OFF the band
        # Else keep the band ON
        if current_band_status == "Up":
            for prediction in inferences:
                if prediction.status:
                    logger.info(f"Station {prediction.station} inference requires the band ON, the 5GHz band remains ON")
                    return current_band_status
            logger.info(f"Setting 5GHz band OFF")
            self.set_band_status(new_status=False)
            return current_band_status

        # If the 5 GHz band is OFF:
        # If for at least one stations the inference result is ON -> then turn ON the band
        # Else keep the band OFF
        else:
            for prediction in inferences:
                if prediction.status:
                    logger.info(f"Station {prediction.station} inference requires the band ON")
                    logger.info(f"Setting 5GHz band ON")
                    self.set_band_status(new_status=True)
                    return current_band_status
            logger.info(f"5GHz band will remain OFF")
            return current_band_status

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
            self.dont_update_band_status_until = datetime.now() + timedelta(minutes=self.band_uptime_in_minutes)

        # Retrieve path and params
        path = "Device.WiFi.Radio.2"
        params = {"Enable": "1"} if new_status else {"Enable": "0"}

        logger.info(f"Setting wifi 5GHz band status to {new_status}")

        self.amx_usp_interface.set_object(path=path, params=params)

        return


wifi_5GHz_band_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
