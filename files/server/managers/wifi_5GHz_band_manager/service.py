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

wifi_5GHz_band_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
