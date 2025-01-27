""" App initialization module."""

import logging
from logging.config import dictConfig
import os
import json
from flask import Flask

# Managers
from server.managers.wifi_5GHz_band_manager import wifi_5GHz_band_manager_service
from server.managers.box_counters_manager import box_counters_manager_service

# Rest APIs
from server.rest_api.wifi_controller import bp as wifi_controller_bp

# Common
from server.common import ServerBoxException, handle_server_box_exception

logger = logging.getLogger(__name__)


def create_app(
    config_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config"),
):
    """Create the Flask app"""

    # Create app Flask
    app = Flask("Orange SLN 5GHz on/off Application")

    # Get server configuration files
    if os.getenv("FLASK_ENV") == "DEVELOPMENT":
        app_config = os.path.join(config_dir, "general-config-development.json")
        logging_config = os.path.join(config_dir, "logging-config-development.json")
    else:
        app_config = os.path.join(config_dir, "general-config.json")
        logging_config = os.path.join(config_dir, "logging-config.json")

    # Load app configuration
    with open(app_config, encoding="utf-8") as config_file:
        config = json.load(config_file)
        app.config.update(config)

    if "SERVER_PORT" not in app.config:
        app.config["SERVER_PORT"] = 5000

    # Load logging configuration and configure flask application logger
    with open(logging_config, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        dictConfig(config)

    logger.info(f"App config file: {app_config}")
    logger.info(f"Logging config file: {logging_config}")

    # Register extensions
    register_extensions(app)
    # Register REST APIs
    register_apis(app)

    logger.info("App ready!!")

    return app


def register_extensions(app: Flask):
    """Initialize all extensions"""
    # Wifi bands manager extension
    wifi_5GHz_band_manager_service.init_app(app=app)
    # Box counters manager extension
    box_counters_manager_service.init_app(app=app)


def register_apis(app: Flask):
    """Store App APIs blueprints."""
    # Register error handler
    app.register_error_handler(ServerBoxException, handle_server_box_exception)
    # Register REST blueprints
    app.register_blueprint(wifi_controller_bp, url_prefix="/api")
