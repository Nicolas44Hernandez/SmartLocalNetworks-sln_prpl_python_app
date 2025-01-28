"""Box counters manager"""

import os
import logging
import threading
import time
from datetime import datetime
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import ServerBoxException, ErrorCode
from server.common.model import stationStatsSample, boxStatsSample, samples_queue

if os.getenv("FLASK_ENV") == "DEVELOPMENT":
    from server.common.mock_dev import mock_stations, mock_radio_air_stats, mock_radio_stats

logger = logging.getLogger(__name__)

class CountersManager(threading.Thread):
    """Manager for box counters poll"""

    amx_usp_interface: AmxUspInterface
    running: bool
    polling_period_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize CountersManager"""
        if app is not None:
            logger.info("initializing the CountersManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()
            self.running = False
            self.polling_period_in_secs = app.config["COUNTERS"]["POLLING_PERIOD_IN_SECS"]

            # Run Counters sample dedicated thread
            super(CountersManager, self).__init__(name="BoxCountersPollThread")
            self.setDaemon(True)
            logger.info("Running counters poll loop in dedicated thread")
            self.start()

    def get_service_status(self):
        """Get running service status"""
        return self.running

    def stop_service(self):
        """Stop service"""
        self.running = False

    def start_service(self):
        """Stop thead"""
        self.running = True

    def run(self):
        """Run thread"""
        while True:
            if self.running:
                # Poll connected stations counters
                start = datetime.now()
                connected_stations_counters = box_counters_manager_service.get_connected_stations_counters()
                # Poll box counters
                box_counters = box_counters_manager_service.get_box_counters()
                end = datetime.now()
                delta = end - start
                samples_queue.put({"box_counters" : box_counters, "stations_counters": connected_stations_counters })
            waitting_time = self.polling_period_in_secs - delta.total_seconds() if self.running else self.polling_period_in_secs
            time.sleep(waitting_time)

    def get_box_radio_stats(self) -> dict:
        """Execute command to get box stats"""
        logger.debug(f"Getting box radio stats")
        if os.getenv("FLASK_ENV") != "DEVELOPMENT":
            try:
                radio_stats = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.*", method="getRadioStats")
                radio_stats_2GHz = radio_stats[2]
                radio_stats_5GHz = radio_stats[0]
            except ServerBoxException as e:
                logger.error("Error when retreiving 5GHz band stats")
                logger.error(e)
                return None
        else:
            radio_stats_2GHz = mock_radio_stats
            radio_stats_5GHz = mock_radio_stats

        result = {"2.4GHz": radio_stats_2GHz[0], "5GHz": radio_stats_5GHz[0]}
        return result

    def get_box_radio_air_stats(self) -> dict:
        """Execute command to get air stats"""
        logger.debug(f"Getting box air stats")
        if os.getenv("FLASK_ENV") != "DEVELOPMENT":
            try:
                radio_air_stats = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.*", method="getRadioAirStats")
                radio_air_stats_2GHz = radio_air_stats[2]
                radio_air_stats_5GHz = radio_air_stats[0]
            except ServerBoxException as e:
                logger.error("Error when retreiving 5GHz band air stats")
                logger.error(e)
                return None
        else:
            radio_air_stats_2GHz = mock_radio_air_stats
            radio_air_stats_5GHz = mock_radio_air_stats

        result = {"2.4GHz": radio_air_stats_2GHz[0], "5GHz": radio_air_stats_5GHz[0]}
        return result

    def get_box_counters(self) -> boxStatsSample:
        """Get box radio counters"""
        # Retreive stats
        box_radio_stats = self.get_box_radio_stats()
        box_radio_air_stats = self.get_box_radio_air_stats()

        # Healt check
        if box_radio_stats is None or box_radio_air_stats is None:
            logger.error("Error retreiving box stats")
            # TODO: Error management
            return None

        box_radio_stats_2GHz = box_radio_stats["2.4GHz"]
        box_radio_stats_5GHz = box_radio_stats["5GHz"]
        box_radio_air_stats_2GHz = box_radio_air_stats["2.4GHz"]
        box_radio_air_stats_5GHz  = box_radio_air_stats["5GHz"]
        timestamp = datetime.now()

        # Create boxStatsSample 2GHz object
        box_stats_sample_2GHz = boxStatsSample(
            timestamp=timestamp,
            bytesReceived=box_radio_stats_2GHz["BytesReceived"],
            bytesSent=box_radio_stats_2GHz["BytesSent"],
            noise=box_radio_stats_2GHz["Noise"],
            load=box_radio_air_stats_2GHz["Load"],
            freeTime=box_radio_air_stats_2GHz["FreeTime"],
            rxTime=box_radio_air_stats_2GHz["RxTime"],
            vendorStats_glitch=box_radio_air_stats_2GHz["VendorStats"]["Glitch"],
            obssTime=box_radio_air_stats_2GHz["ObssTime"],
            txTime=box_radio_air_stats_2GHz["TxTime"],
            intTime=box_radio_air_stats_2GHz["IntTime"],
            noise_air=box_radio_air_stats_2GHz["Noise"],
            packetsReceived=box_radio_stats_2GHz["PacketsReceived"],
            packetsSent=box_radio_stats_2GHz["PacketsSent"],
            errorsReceived=box_radio_stats_2GHz["ErrorsReceived"],
            errorsSent=box_radio_stats_2GHz["ErrorsSent"],
        )
        logger.debug(f"\nbox_stats_sample_2GHz:{box_stats_sample_2GHz}\n")

        # Create boxStatsSample 5GHz object
        box_stats_sample_5GHz = boxStatsSample(
            timestamp=timestamp,
            bytesReceived=box_radio_stats_5GHz["BytesReceived"],
            bytesSent=box_radio_stats_5GHz["BytesSent"],
            noise=box_radio_stats_5GHz["Noise"],
            load=box_radio_air_stats_5GHz["Load"],
            freeTime=box_radio_air_stats_5GHz["FreeTime"],
            rxTime=box_radio_air_stats_5GHz["RxTime"],
            vendorStats_glitch=box_radio_air_stats_5GHz["VendorStats"]["Glitch"],
            obssTime=box_radio_air_stats_5GHz["ObssTime"],
            txTime=box_radio_air_stats_5GHz["TxTime"],
            intTime=box_radio_air_stats_5GHz["IntTime"],
            noise_air=box_radio_air_stats_5GHz["Noise"],
            packetsReceived=box_radio_stats_5GHz["PacketsReceived"],
            packetsSent=box_radio_stats_5GHz["PacketsSent"],
            errorsReceived=box_radio_stats_5GHz["ErrorsReceived"],
            errorsSent=box_radio_stats_5GHz["ErrorsSent"],
        )
        logger.debug(f"\nbox_stats_sample_5GHz:{box_stats_sample_5GHz}\n")

        # Return counters
        return {"2.4GHz": box_stats_sample_2GHz, "5GHz": box_stats_sample_5GHz}

    def get_connected_stations_stats(self) -> dict:
        """Execute command to get connected stations stats"""
        connected_stations = {}
        cmd = "Device.WiFi.AccessPoint.*.AssociatedDevice."
        logger.debug(f"Getting active stations stats - cmd:{cmd}")
        if os.getenv("FLASK_ENV") != "DEVELOPMENT":
            try:
                stations = self.amx_usp_interface.read_object(path=cmd)[0]
            except ServerBoxException:
                logger.error("Error when retreiving connected stations counters")
                return None
        else:
            stations = mock_stations

        # Loop in stations to get active stations
        for key in stations:
            band = "5GHz" if int(key.split("AccessPoint.")[1][0]) == 1 else "2.4GHz"
            # Get station status (active/inactive)
            _active = True if stations[key]["Active"] == 1 else False
            if _active:
                # Append band to station dict
                stations[key]["band"] = band
                # Get station mac address
                _mac_address = stations[key]["MACAddress"]
                connected_stations[_mac_address] = stations[key]

        # Return connected stations dict
        return connected_stations

    def get_connected_stations_counters(self):
        """Get connected stations counters"""
        # Retreive connected stations stats
        stations_stats = self.get_connected_stations_stats()
        timestamp = datetime.now()
        stations_counters = {}

        # Healt check
        if stations_stats is None:
            logger.error("Error retreiving connected stations stats")
            # TODO: Error management
            return None

        # loop over connected stations
        for station in stations_stats:
            # Create and append stationStatsSample object
            stations_counters[station] = stationStatsSample(
                timestamp=timestamp,
                txBytes=stations_stats[station]["TxBytes"],
                rxBytes=stations_stats[station]["RxBytes"],
                uplinkMCS=stations_stats[station]["UplinkMCS"],
                lastDataUplinkRate=stations_stats[station]["LastDataUplinkRate"],
                lastDataDownlinkRate=stations_stats[station]["LastDataDownlinkRate"],
                signalStrength=stations_stats[station]["SignalStrength"],
                avgSignalStrengthByChain=stations_stats[station]["AvgSignalStrengthByChain"],
                uplinkShortGuard=stations_stats[station]["UplinkShortGuard"],
                downlinkMCS=stations_stats[station]["DownlinkMCS"],
                signalNoiseRatio=stations_stats[station]["SignalNoiseRatio"],
                rxPacketCount=stations_stats[station]["RxPacketCount"],
                txPacketCount=stations_stats[station]["TxPacketCount"],
            )

        # Return stations counters sample list
        return stations_counters

box_counters_manager_service: CountersManager = CountersManager()
""" Box Countrers manager service singleton"""
