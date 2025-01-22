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

Install gfortran in the container
```bash
sudo apt install gfortran
```

Add fortran to sdk local.conf file
```bash
FORTRAN:forcevariable = ",fortran"
RUNTIMETARGET:append:pn-gcc-runtime = " libquadmath"
HOSTTOOLS += "gfortran"
```

Append this line to openblas_%.bbappend
```bash
PACKAGECONFIG = "lapack cblas affinity dynarch"
```

Add expertice-center-layers (from host)
```bash
cd workspace/layers/
git clone git@gitlab.tech.orange:prpl-ware/samples/meta-expertisecenter_prpl.git
cd meta-expertisecenter_prpl
git checkout add_scarthgap_compatibility
```

and from container
```bash
sed -i 's#${SDKBASEMETAPATH}/workspace \\$#${SDKBASEMETAPATH}/layers/meta-expertisecenter_prpl \\\n    ${SDKBASEMETAPATH}/workspace \\ #g' /sdkworkdir/conf/bblayers.conf
```

Clone app repo (from host)
```bash
cd recipes-example
git clone https://github.com/Nicolas44Hernandez/SmartLocalNetworks-sln_prpl_python_app.git
```

Add the dependencies recipes
```bash
devtool modify python-amx
devtool modify python3-flask
devtool modify python3-joblib
devtool modify python3-pandas
devtool modify python3-scikit-learn
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
ubus-cli "SoftwareModules.InstallDU(URL = 'docker://<REGISTRY>:<TAG>', Username = <USER>, Password = <PASSWORD>, ExecutionEnvRef = 'generic', UUID = 'aade1eee-8ee1-5690-887f-b41aab7ca15e', NetworkConfig = {"AccessInterfaces" = [{"Reference" = "Lan"}],  "PortForwarding" = [{"Interface" = "Lan", "ExternalPort" = 8000, "InternalPort" = 6060, "Protocol" = "TCP"}]})"
```
## Configure permission
To allow the container to access to datamodel, it is necessary to allow it. It is also for exposure on host or get a information from the host.

Create and configure controller to access to datamodel (from prpl device)
```bash
ubus-cli 'LocalAgent.Controller.+{Alias = "python-usp", AssignedRole = "Device.LocalAgent.ControllerTrust.Role.2", Enable=1, EndpointID = "proto::python-usp"}'
ubus-cli 'LocalAgent.Controller.python-usp.MTP+{Alias = "mtp-uds", Enable=1, Protocol = "UDS"}'
```

Add datamodel permisions to container
```bash
ubus-cli 'LocalAgent.ControllerTrust.Role.2.Permission.+{Alias = "my-permissions", CommandEvent = "rwxn", Enable=true, InstantiatedObj = "rwxn", Obj = "rwxn", Order=1, Param="rwxn", Targets="Device.DeviceInfo.,Device.WiFi."}'
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
curl 192.168.102.1:8000/api/wifi
```

# UNINSTALL
```bash
ubus-cli "SoftwareModules.DeploymentUnit.cpe-<IMAGE>.Uninstall(RetainData = "No")"
```
