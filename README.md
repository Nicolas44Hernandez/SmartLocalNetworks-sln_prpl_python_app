# SmartLocalNetworks-sln_prpl_python_app
Prpl python app

## Build the image
Clone recipe in prpl_sdk_lb6:
```bash
git clone https://github.com/Nicolas44Hernandez/SmartLocalNetworks-sln_prpl_python_app.git
```

Run the sdk helper 
```bash
~/sdk_helper/prpl-sdk
```

Add the dependencies recipes 
```bash
devtool modify python-amx
devtool modify python3-joblib
devtool modify python3-pandas
devtool modify python3-flask
devtool modify python3-yamlloader
devtool modify python3-flask-restful
``` 

Add the recipe
```bash
devtool modify sln-py
``` 

Build the project 
```bash
devtool build sln-py
``` 

Build image 
```bash
devtool build-image
``` 

## Publish the image

Publish image to registry
```bash
user@prplSDK sdkworkdir$ skopeo copy oci:/sdkworkdir/tmp/deploy/images/container-cortexa53/image-lcm-container-minimal-container-cortexa53.rootfs-oci docker://<REGISTRY>/sln-py --dest-creds=<USER>:<PASSORD>

``` 

## Install the image
Connect to Prpl device

```bash
ubus-cli "SoftwareModules.InstallDU(URL = 'docker://<REGISTRY>/sln-py', Username = <USER> , Password = <PASSWORD>, ExecutionEnvRef = 'generic', UUID = 'aade1eee-8ee1-5690-887f-b41aab7ca15e')"

``` 
## Configure permission
To allow the container to access to datamodel, it is necessary to allow it. It is also for exposure on host or get a information from the host.
First, get the endpointID of the container, the container name is the DUID or UUID depending of the platform

```bash
lxc-attach -n <DUID|UUID> -- ubus-cli 'LocalAgent.EndpointID?' | grep LocalAgent.EndpointID
```

Check if there is a Controller for the container
```bash
ubus-cli 'LocalAgent.Controller.?' | grep <DUID|UUID>
```

If there is no result create the Controller
```bash
ubus-cli 'LocalAgent.Controller.+{Alias = "controller-<DUID>", AssignedRole = "Device.LocalAgent.ControllerTrust.Role.2", Enable=1, EndpointID = "<ENDPOINT_ID_CONTAINER>"}'
```

Add the MTP configuration
```bash
ubus-cli 'LocalAgent.Controller.controller-<DUID>.MTP+{Alias = "mtp-uds", Enable=1, Protocol = "UDS"}'
```

If the Controller already exist, add the operator role to the container, replace the controller-<DUID> with the DUID
```bash
ubus-cli 'LocalAgent.Controller.controller-1c4f86b1-35ec-5a2c-997a-f1fa9271b8bf.AssignedRole="Device.LocalAgent.ControllerTrust.Role.2"'
```

Add the choosen permission for the given role.
```bash
ubus-cli 'LocalAgent.ControllerTrust.Role.2.Permission.+{Alias = "my-permissions", CommandEvent = "rwxn", Enable=true, InstantiatedObj = "rwxn", Obj = "rwxn", Order=1, Param="rwxn", Targets="Device.WiFi.Radio."}'
``` 

If the ControllerTrust.Role doesn't exist it is possible to add it
```bash
ubus-cli 'LocalAgent.ControllerTrust.Role+{Alias = "operator", Enable = true, Name = "operator"}'
``` 

NB if the field already exist, only change the Targets or change parameters manually
```bash
ubus-cli 'LocalAgent.ControllerTrust.Role.2.Permission.1.Targets="Device.DeviceInfo.,Device.X_Orange_Demo.
``` 

## Run the application 
TODO
Connect to the Prpl device.
Attach to container
```bash
lxc-ls --fancy
lxc-attach <DUID>
```

run the application 
```bash
cd /usr/srv/
export FLASK_APP="server/app:create_app()"
export FLASK_ENV="development"
flask run --host '0.0.0.0' --port 6060
```

## Test the rest apis
From a device connected to the lan 
```bash
curl 192.168.102.1:8000/wifi/status
```

# UNINSTALL 
```bash
ubus-cli "SoftwareModules.DeploymentUnit.cpe-<IMAGE>.Uninstall(RetainData = "No")"
```

# TODO:
- [ ] Add prpl expertice center links to docs