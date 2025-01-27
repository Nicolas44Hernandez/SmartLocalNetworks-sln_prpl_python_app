"""REST API Wifi controler package"""
from .rest_controller import bp, WifiStatusApi, BoxRadioStatsApi, BoxRadioAirStatsApi, ConnectedStationsStatsApi, BoxCountersApi
bp.add_url_rule("/wifi", view_func=WifiStatusApi.as_view("wifi_api"))
bp.add_url_rule("/wifi/box/counters", view_func=BoxCountersApi.as_view("wifi_box_counters_api"))
bp.add_url_rule("/wifi/counters/stats", view_func=BoxRadioStatsApi.as_view("wifi_box_radio_stats_api"))
bp.add_url_rule("/wifi/counters/air-stats", view_func=BoxRadioAirStatsApi.as_view("wifi_box_radio_air_stats_api"))
bp.add_url_rule("/wifi/counters/stations/stats", view_func=ConnectedStationsStatsApi.as_view("wifi_box_stations_stats_api"))

