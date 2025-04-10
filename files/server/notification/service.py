"""Notification service """

import logging
import json
import threading
import http.client
import urllib.parse
from flask import Flask
from datetime import datetime
from typing import Iterable
from server.common import boxCounters, StationCounters, SingleStationInferenceResult, boxStatsSample, stationStatsSample, InferencesInput

POST_TIMEOUT_IN_SECS = 2


logger = logging.getLogger(__name__)


class Notification():
    """Notification service"""

    web_server_ip_addr: str
    web_server_port: int
    web_server_general_notification_path: str
    web_server_band_status_notification_path: str
    web_server_stations_traffic_notification_path: str
    web_server_box_counters_notification_path: str
    web_server_stations_counters_notification_path: str
    web_server_inferences_results_notification_path: str


    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_notification_module(app)

    def init_notification_module(self, app: Flask ):
        """Initialize the notification service"""

        if app is not None:
            logger.info("initializing  notification module")

        self.web_server_ip_addr = app.config["WEB_SERVER"]["IP_ADDRESS"]
        self.web_server_port = app.config["WEB_SERVER"]["PORT"]
        self.web_server_general_notification_path = app.config["WEB_SERVER"]["PATHS"]["GENERAL_NOTIFICATION"]
        self.web_server_band_status_notification_path = app.config["WEB_SERVER"]["PATHS"]["BAND_STATUS"]
        self.web_server_box_traffic_notification_path = app.config["WEB_SERVER"]["PATHS"]["BOX_TRAFFIC"]
        self.web_server_stations_traffic_notification_path = app.config["WEB_SERVER"]["PATHS"]["STATIONS_TRAFFIC"]
        self.web_server_box_counters_notification_path = app.config["WEB_SERVER"]["PATHS"]["BOX_COUNTERS"]
        self.web_server_stations_counters_notification_path = app.config["WEB_SERVER"]["PATHS"]["STATIONS_COUNTERS"]
        self.web_server_inferences_results_notification_path = app.config["WEB_SERVER"]["PATHS"]["INFERENCES_RESULTS"]


    def notify_sample_to_web_server(
        self,
        band_status: bool,
        box_counter_2GHz: boxCounters,
        box_counter_5GHz: boxCounters,
        stations_counters: Iterable[StationCounters],
        inferences_input: InferencesInput,
        inferences_results: Iterable[SingleStationInferenceResult],
        timestamp: datetime
    ):
        """Notify sample to web server"""

        logger.debug("Posting HTTP to notify sample to web server")

        # Notify in separated http post, each post in independent thread

        # Convert timestamp
        timestamp_str = timestamp.isoformat(timespec='milliseconds') + 'Z'

        # Notify band status
        self.notify_band_status(band_status=band_status, timestamp_str=timestamp_str)

        # Notify box traffic
        if len(box_counter_2GHz.tx_Mbps) > 0:
            self.notify_box_traffic(box_counter_2GHz=box_counter_2GHz, box_counter_5GHz=box_counter_5GHz, timestamp_str=timestamp_str)

        # Notify stations traffic
        if len(stations_counters) > 0:
            self.notify_stations_traffic(stations_counters=stations_counters, timestamp_str=timestamp_str)

        # Notify inferences results
        if len(inferences_results) > 0:
            self.notify_inferences(inferences_input=inferences_input, inferences_results=inferences_results, timestamp_str=timestamp_str)



    def notify_band_status(self, band_status: bool, timestamp_str: str):
        """Notify band status in dedicated thread"""

        self.http_post_in_dedicated_thread(
            url=self.web_server_ip_addr,
            port=self.web_server_port,
            endpoint=self.web_server_band_status_notification_path,
            data={
                "timestamp": timestamp_str,
                "status" : band_status,
            },
        )

    def notify_box_traffic(self, box_counter_2GHz: boxCounters, box_counter_5GHz:boxCounters, timestamp_str: str):
        """Notify box traffic in dedicated thread"""

        self.http_post_in_dedicated_thread(
            url=self.web_server_ip_addr,
            port=self.web_server_port,
            endpoint=self.web_server_box_traffic_notification_path,
            data={
                "timestamp": timestamp_str,
                "band": "2.4GHz",
                "rx_Mbps": box_counter_2GHz.rx_Mbps[-1],
                "tx_Mbps": box_counter_2GHz.tx_Mbps[-1],
            }
        )
        # If 5GHz band is ON notify traffic
        if box_counter_5GHz is not None:
            self.http_post_in_dedicated_thread(
                url=self.web_server_ip_addr,
                port=self.web_server_port,
                endpoint=self.web_server_box_traffic_notification_path,
                data={
                    "timestamp": timestamp_str,
                    "band": "5GHz",
                    "rx_Mbps": box_counter_5GHz.rx_Mbps[-1],
                    "tx_Mbps": box_counter_5GHz.tx_Mbps[-1],
                }
            )

    def notify_stations_traffic(self, stations_counters: Iterable[StationCounters], timestamp_str: str):
        """Notify stations traffic in dedicated thread"""

        stations_traffic = []
        for station in stations_counters:
            if len(stations_counters[station].tx_Mbps) > 0:
                stations_traffic.append(
                    {
                    "timestamp": timestamp_str,
                    "station": station,
                    "rx_Mbps": stations_counters[station].rx_Mbps[-1],
                    "tx_Mbps": stations_counters[station].tx_Mbps[-1],
                    }
                )

        self.http_post_in_dedicated_thread(
            url=self.web_server_ip_addr,
            port=self.web_server_port,
            endpoint=self.web_server_stations_traffic_notification_path,
            data=stations_traffic
        )

    def notify_box_counters(self, box_counters: boxStatsSample):
        """Notify box counters in dedicated thread"""

        self.http_post_in_dedicated_thread(
            url=self.web_server_ip_addr,
            port=self.web_server_port,
            endpoint=self.web_server_box_counters_notification_path,
            data=box_counters.to_dict(),
        )

    def notify_stations_counters(self, stations_counters: Iterable[stationStatsSample]):
        """Notify stations counters in dedicated thread"""

        data = [counters.to_dict() for counters in stations_counters]

        self.http_post_in_dedicated_thread(
            url=self.web_server_ip_addr,
            port=self.web_server_port,
            endpoint=self.web_server_stations_counters_notification_path,
            data=data,
        )

    def notify_inferences(
            self,
            inferences_input: InferencesInput,
            inferences_results: Iterable[SingleStationInferenceResult],
            timestamp_str: str,
        ):

        """Notify inferences results in dedicated thread"""
        data = []
        for station_data, inference_result in zip(inferences_input.stations_data, inferences_results):
            # Create inference dict
            inference_dict = {}
            # Extract station
            inference_dict["station"] = station_data.station
            # Extract station inference input data
            input_data_dict = station_data.to_dict()
            # Remove station key:value from station dict
            del input_data_dict['station']
            # Extract box inference input data
            box_input_data_dict = inferences_input.box_data.to_dict()
            # Fusion station input data and box input data
            input_data_dict.update(box_input_data_dict)
            # Extract result data
            inference_result_dict = inference_result.to_dict()
            del inference_result_dict['station']

            # Append to inference dict
            inference_dict["input"] = input_data_dict
            inference_dict["result"] = inference_result_dict
            inference_dict["timestamp"] = timestamp_str

            # Append inference dict to data to post
            data.append(inference_dict)

        self.http_post_in_dedicated_thread(
            url=self.web_server_ip_addr,
            port=self.web_server_port,
            endpoint=self.web_server_inferences_results_notification_path,
            data=data,
        )

    def http_post(
        self, url: str, port: int, endpoint: str, data: dict, timeout: int = POST_TIMEOUT_IN_SECS
    ):
        """HTTP Post"""
        try:
            # Convert the data to JSON format
            json_data = json.dumps(data)
            # Create a connection
            logger.debug(f"Connecting to url: {url} port: {port}")
            conn = http.client.HTTPConnection(url, port, timeout=timeout)
            # Make the headers
            headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            # Make the post request
            conn.request("POST", endpoint, body=json_data, headers=headers)
            # Get the response
            response = conn.getresponse()
            logger.debug(f"Server response status: {response.status}")
            if response.status != 201:
                logger.error(
                    f"Error when posting to web server: {response.status} - {response.reason}"
                )
        except (http.client.HTTPException, OSError) as e:
            logger.error(f"Error when posting to web server: {e}")

    def http_post_in_dedicated_thread(
        self, url: str, port: int, endpoint: str, data: dict, timeout: int = POST_TIMEOUT_IN_SECS
    ):
        """HTTP Post in dedicated thread"""

        post_thread = threading.Thread(
            target=self.http_post,
            args=[url, port, endpoint, data, timeout],
            name="NotificationHttpPost",
        )
        post_thread.start()


notification_service: Notification = Notification()
""" Notification service singleton"""
