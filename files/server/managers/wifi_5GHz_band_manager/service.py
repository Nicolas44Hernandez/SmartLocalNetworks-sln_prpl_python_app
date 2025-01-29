"""Wifi Bands manager"""

import logging
import threading
import queue
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import samples_queue

logger = logging.getLogger(__name__)

BANDS = ["2.4GHz", "5GHz", "6GHz"]

class WifiBandsManager(threading.Thread):
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
                logger.info(f"Sample received in queue: {sample}\n\n\n\n")
                # TODO: perform inference


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
