import pamx

FIELD = "Device.DeviceInfo.FriendlyName"

# load usp backend
pamx.backend.load("/usr/bin/mods/amxb/mod-amxb-usp.so")
# set a endpointID to have an easy configuration
pamx.backend.set_config({"usp" : {"EndpointID": "proto::python-usp"}})
# connect to the bus
connection = pamx.bus.connect("usp:/var/run/imtp/broker_agent_path")
# get FriendlyName
print(connection.get("Device.DeviceInfo.FriendlyName"))
# change FriendlyName
connection.set("Device.DeviceInfo", {"FriendlyName": "test-usp-python"})
# get again the FriendlyName
print(connection.get("Device.DeviceInfo.FriendlyName"))

