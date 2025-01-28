"""REst API for WiFi controller"""

import logging
from flask import Blueprint, jsonify, request
from flask.views import MethodView
from server.managers.wifi_5GHz_band_manager import wifi_5GHz_band_manager_service
from server.managers.box_counters_manager import box_counters_manager_service
from server.common import ServerBoxException, ErrorCode
from server.rest_api.common import add_cors

logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__)


class WifiStatusApi(MethodView):
    """API to retrieve wifi general status"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET api/wifi/")
        status = wifi_5GHz_band_manager_service.get_band_status()

        response = jsonify({"status": status})

        return add_cors(response)

class BoxRadioStatsApi(MethodView):
    """API to retrieve box stats data"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET api/wifi/counters/stats")
        box_stats = box_counters_manager_service.get_box_radio_stats()

        response = jsonify({"box_radio_stats": box_stats})

        return add_cors(response)

class BoxRadioAirStatsApi(MethodView):
    """API to retrieve box stats data"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET api/wifi/counters/air-stats")
        box_stats = box_counters_manager_service.get_box_radio_air_stats()

        response = jsonify({"box_radio_air_stats": box_stats})

        return add_cors(response)

class ConnectedStationsStatsApi(MethodView):
    """API to retrieve connected stations stats data"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET api/wifi/counters/stations")
        stations_stats = box_counters_manager_service.get_connected_stations_stats()

        response = jsonify({"connected_stations_stats": stations_stats})

        return add_cors(response)

class BoxCountersApi(MethodView):
    """API to retrieve box stats data"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET api/wifi/counters/sample/box")
        box_stats = box_counters_manager_service.get_box_counters()

        response = jsonify({"box_counters": box_stats})

        return add_cors(response)

class ConnectedStationsCountersApi(MethodView):
    """API to retrieve connected stations counters data"""

    def get(self):
        """Get connected stations sample counter"""
        logger.info("GET api/wifi/counters/sample/stations")
        stations_counters = box_counters_manager_service.get_connected_stations_counters()

        response = jsonify({"stations_counters": stations_counters})

        return add_cors(response)

class SlnServiceApi(MethodView):
    """API to manage automatic 5GHz on/off service"""

    def get(self):
        """Get livebox wifi 5GHz status"""
        logger.info("GET api/wifi/sln/status")

        service_status = box_counters_manager_service.get_service_status()

        response = jsonify({"status": service_status})

        return add_cors(response)

    def post(self):
        """
        Set service status
        """
        logger.info("POST api/wifi/sln/status")

        # Retrieve query args
        new_status_from_query = request.args.get("new_status", default=None)
        # Convert to boolean
        if new_status_from_query is not None:
            if new_status_from_query.lower() in ["true", "1", "yes", "up"]:
                new_status = True
            elif new_status_from_query.lower() in ["false", "0", "no", "down"]:
                new_status = False
            else:
                raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS)
        else:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS)

        # Retrieve current status
        current_status = box_counters_manager_service.get_service_status()
        logger.info(f"Setting SLN service status: {new_status}")

        # If new status is already satisfied
        if current_status == new_status:
            logger.info(f"Service status is already: {current_status}")
            response = jsonify({"status": current_status})

        else:
            logger.info(f"Setting service status to: {new_status}")
            if new_status:
                box_counters_manager_service.start_service()
            else:
                box_counters_manager_service.stop_service()

            response = jsonify({"status": new_status})

        return add_cors(response)
