"""REST API Wifi controler package"""
from .rest_controller import bp, WifiStatusApi, BoxRadioStatsApi, BoxRadioAirStatsApi, ConnectedStationsStatsApi, BoxCountersApi, ConnectedStationsCountersApi, SlnServiceApi
bp.add_url_rule("/wifi", view_func=WifiStatusApi.as_view("wifi_api"))
bp.add_url_rule("/wifi/counters/stats", view_func=BoxRadioStatsApi.as_view("wifi_box_radio_stats_api"))
bp.add_url_rule("/wifi/counters/air-stats", view_func=BoxRadioAirStatsApi.as_view("wifi_box_radio_air_stats_api"))
bp.add_url_rule("/wifi/counters/stations", view_func=ConnectedStationsStatsApi.as_view("wifi_box_stations_stats_api"))
bp.add_url_rule("/wifi/counters/sample/box", view_func=BoxCountersApi.as_view("wifi_box_counters_api"))
bp.add_url_rule("/wifi/counters/sample/stations", view_func=ConnectedStationsCountersApi.as_view("wifi_stations_counters_api"))
bp.add_url_rule("/wifi/sln/status", view_func=SlnServiceApi.as_view("wifi_sln_service_status_api"))

