"""REst API for WiFi controller"""

import logging
from flask import Blueprint, jsonify, request
from flask.views import MethodView
from server.managers.wifi_5GHz_band_manager import wifi_5GHz_band_manager_service
from server.common import ServerBoxException, ErrorCode
from server.rest_api.common import add_cors

logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__)


class WifiStatusApi(MethodView):
    """API to retrieve wifi general status"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET wifi/")
        status = wifi_5GHz_band_manager_service.get_band_status()

        response = jsonify({"status": status})

        return add_cors(response)

class BoxRadioStatsApi(MethodView):
    """API to retrieve box stats data"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET wifi/radio/stats")
        box_stats = wifi_5GHz_band_manager_service.get_box_radio_stats()

        response = jsonify({"box_radio_stats": box_stats})

        return add_cors(response)

class BoxRadioAirStatsApi(MethodView):
    """API to retrieve box stats data"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET wifi/radio/air-stats")
        box_stats = wifi_5GHz_band_manager_service.get_box_radio_air_stats()

        response = jsonify({"box_radio_air_stats": box_stats})

        return add_cors(response)
