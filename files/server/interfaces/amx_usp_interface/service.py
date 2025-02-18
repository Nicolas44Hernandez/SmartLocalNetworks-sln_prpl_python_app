"""AMX USP interface package"""

import logging
from server.common import ServerBoxException, ErrorCode

try:
    import pamx
except ModuleNotFoundError:
    pamx = None  # pylint: disable=C0103


logger = logging.getLogger(__name__)


class AmxUspClient:
    """Service class for AmxUsp interface"""

    def __init__(self):
        logger.debug("initializing the AmxUspClient")
        if pamx is not None:
            try:
                pamx.backend.load("/usr/bin/mods/amxb/mod-amxb-usp.so")
                pamx.backend.set_config({"usp" : {"EndpointID": "proto::python-usp"}})
                self.connection = pamx.bus.connect("usp:/var/run/imtp/broker_agent_path")
            except Exception as exc:
                raise ServerBoxException(ErrorCode.USP_LOAD_ERROR) from exc

    # Python AMX functions : get/set/add/delete
    def read_object(self, path: str):
        """Read USP Object"""
        logger.debug(f"AMX USP Read object: {path}")
        if pamx is not None:
            try:
                return self.connection.get(path)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.USP_ERROR) from exc

    def exec_method(self, obj:str, method: str):
        """Exec USP method"""
        logger.debug(f"AMX USP Execute method: {obj}.{method}")
        if pamx is not None:
            try:
                return self.connection.call(obj, method)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.USP_ERROR) from exc


    def set_object(self, path: str, params: dict):
        """Set USP Object"""
        logger.debug(f"AMX USP Set object: {path}  params: {params}")
        if pamx is not None:
            try:
                return self.connection.set(path, params)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.USP_ERROR) from exc

    def add_object(self, path, params: dict):
        """Add USP Object"""
        logger.debug(f"AMX USP Add object: {path}  params: {params}")
        if pamx is not None:
            try:
                return self.connection.add(path, params)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.USP_ERROR) from exc

    def del_object(self, path: str):
        """Delete USP Object"""
        logger.debug(f"AMX USP Delete object: {path}")
        if pamx is not None:
            try:
                return self.connection.delete(path)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.USP_ERROR) from exc
