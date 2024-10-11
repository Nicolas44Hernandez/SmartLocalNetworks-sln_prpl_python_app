import logging
from flask_restful import Resource
from server.managers.wifi_5GHz_band_manager import wifi_5GHz_band_manager_service 

logger = logging.getLogger(__name__)

class WifiStatusApi(Resource):
    """API to retrieve wifi general status"""

    def get(self):
        """Get livebox wifi status"""
        logger.info("GET wifi/")
        status = wifi_5GHz_band_manager_service.get_band_status(band="5GHz")
        return {"status": status}, 200