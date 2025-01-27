"""Box counters manager"""

import logging
from datetime import datetime
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import ServerBoxException, ErrorCode
from server.common.model import StationCounters, stationStatsSample, boxCounters, boxStatsSample

logger = logging.getLogger(__name__)

class CountersManager:
    """Manager for box counters poll"""

    amx_usp_interface: AmxUspInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize CountersManager"""
        if app is not None:
            logger.info("initializing the CountersManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()


    def get_box_radio_stats(self):
        """Execute command to get box stats"""
        logger.info(f"Getting box radio stats")
        try:
            radio_stats_2GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.1", method="getRadioStats")
            radio_stats_5GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.2", method="getRadioStats")
        except ServerBoxException as e:
            logger.error("Error when retreiving 5GHz band stats")
            logger.error(e)
            return None
        result = {"2.4GHz": radio_stats_2GHz[0], "5GHz": radio_stats_5GHz[0]}
        return result

    def get_box_radio_air_stats(self):
        """Execute command to get air stats"""
        logger.info(f"Getting box air stats")
        try:
            radio_air_stats_2GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.1", method="getRadioAirStats")
            radio_air_stats_5GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.2", method="getRadioAirStats")
        except ServerBoxException as e:
            logger.error("Error when retreiving 5GHz band air stats")
            logger.error(e)
            return None
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
        logger.info(f"\nbox_stats_sample_2GHz:{box_stats_sample_2GHz}\n")

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
        logger.info(f"\nbox_stats_sample_5GHz:{box_stats_sample_5GHz}\n")

        # Return counters
        return {"2.4GHz": box_stats_sample_2GHz, "5GHz": box_stats_sample_5GHz}

    def get_connected_stations_counters(self):
        """Get connected stations counters"""
        connected_stations = {}
        cmd = "Device.WiFi.AccessPoint.*.AssociatedDevice."
        logger.info(f"Getting active stations stats - cmd:{cmd}")
        # Retreive data from datamodel
        try:
            stations = self.amx_usp_interface.read_object(path=cmd)[0]
        except ServerBoxException:
            logger.error("Error when retreiving connected stations counters")
            return None
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

        # Print connected stations mac addresses
        logger.info(f"Connected stations MAC list: {list(connected_stations.keys())}")

        # Return connected stations
        return connected_stations


box_counters_manager_service: CountersManager = CountersManager()
""" Box Countrers manager service singleton"""
