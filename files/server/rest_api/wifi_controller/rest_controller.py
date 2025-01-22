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
        """Get livebox wifi status"""
        logger.info("GET wifi/")
        status = wifi_5GHz_band_manager_service.get_band_status(band="5GHz")

        response = jsonify({"status": status})

        return add_cors(response)
