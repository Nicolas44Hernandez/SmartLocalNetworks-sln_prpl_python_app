import pamx
import json


FIELD  = "Device.WiFi.Radio.1.Status"
OBJ_METHOD  = ("Device.WiFi.Radio.2","getRadioStats()")

class AmxUspClient:
    """Service class for AmxUsp interface"""

    def __init__(self):
        print("initializing the AmxUspClient")
        pamx.backend.load("/usr/bin/mods/amxb/mod-amxb-usp.so")
        pamx.backend.set_config({"usp" : {"EndpointID": "proto::python-usp"}})
        self.connection = pamx.bus.connect("usp:/var/run/imtp/broker_agent_path")

    # Python AMX functions : get/set/add/delete
    def read_object(self, path: str):
        """Read USP Object"""
        print(f"AMX USP Read object: {path}")
        return self.connection.get(path)

    def exec_method(self, obj:str, method: str):
        """Exec USP method"""
        print(f"AMX USP Execute method: {obj}.{method}")
        return self.connection.call(obj, method)

    def set_object(self, path: str, params: dict):
        """Set USP Object"""
        print(f"AMX USP Set object: {path}  params: {params}")
        return self.connection.set(path, json.loads(params))

    def add_object(self, path, params: dict):
        """Add USP Object"""
        print(f"AMX USP Add object: {path}  params: {params}")
        return self.connection.add(path, json.loads(params))

    def del_object(self, path: str):
        """Delete USP Object"""
        print(f"AMX USP Delete object: {path}")
        return self.connection.delete(path)



if __name__ == "__main__":

    # Create interface
    usp_client = AmxUspClient()

    # GET FROM DATAMODEL
    print("GET object")
    # retreive field
    data = usp_client.read_object(path=FIELD)
    print(f"FIELD: {FIELD}")
    print(f"DATA: {data}")

    # EXECUTE METHOD
    print("CALL function")
    obj, method = OBJ_METHOD
    print(f"OBJ: {obj}")
    print(f"DATA: {method}")
    data = usp_client.exec_method(obj=obj, method=method)
    print(f"DATA: {data}")

