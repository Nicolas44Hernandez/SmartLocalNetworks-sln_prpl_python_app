"""REST API Wifi controler package"""
from .rest_controller import bp, WifiStatusApi, BoxRadioStatsApi, BoxRadioAirStatsApi
bp.add_url_rule("/wifi", view_func=WifiStatusApi.as_view("wifi_api"))
bp.add_url_rule("/wifi/radio/stats", view_func=BoxRadioStatsApi.as_view("wifi_box_radio_stats_api"))
bp.add_url_rule("/wifi/radio/air-stats", view_func=BoxRadioAirStatsApi.as_view("wifi_box_radio_air_stats_api"))
