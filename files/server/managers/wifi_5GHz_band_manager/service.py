"""Wifi Bands manager"""

import logging
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import ServerBoxException, ErrorCode


logger = logging.getLogger(__name__)

BANDS = ["2.4GHz", "5GHz", "6GHz"]

class WifiBandsManager:
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

    def get_band_status(self):
        """Execute get wifi band status command in the livebox using AMX USP """
        # Check if band number exists
        #TODO: Validate if band doensnt exists
        cmd = "Device.WiFi.Radio.2.Status"
        logger.info(f"Getting wifi status - {cmd}")
        status = self.amx_usp_interface.read_object(path=cmd)
        logger.info(f"status: {status}")
        return status


    def get_box_radio_stats(self):
        """Execute command to get box stats"""
        logger.info(f"Getting box radio stats")
        try:
            radio_stats_2GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.1", method="getRadioStats")
            radio_stats_5GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.2", method="getRadioStats")
        except ServerBoxException:
            logger.error("Error when retreiving 5GHz band stats")
            return None
        result = {"2.4GHz": radio_stats_2GHz, "5GHz": radio_stats_5GHz}
        return result

    def get_box_radio_air_stats(self):
        """Execute command to get air stats"""
        logger.info(f"Getting box air stats")
        try:
            radio_air_stats_2GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.1", method="getRadioAirStats")
            radio_air_stats_5GHz = self.amx_usp_interface.exec_method(obj="Device.WiFi.Radio.2", method="getRadioAirStats")
        except ServerBoxException:
            logger.error("Error when retreiving 5GHz band stats")
            return None
        result = {"2.4GHz": radio_air_stats_2GHz, "5GHz": radio_air_stats_5GHz}
        return result


wifi_5GHz_band_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
