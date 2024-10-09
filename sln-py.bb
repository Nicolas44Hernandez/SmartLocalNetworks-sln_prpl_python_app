FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://server"


S = "${WORKDIR}"

LICENSE = "CLOSED"
LIC_FILES_CHKSUM = ""

DEPENDS += "python3"
RDEPENDS:${PN} += "python3"


do_configure () {
        # Specify any needed configure commands here
        :
}

do_compile () {
        # Specify compilation commands here
        :
}

do_install () {
        # APP
        install -d ${D}/usr/server        
        install -m 0644 ${S}/server/app.py ${D}/usr/server/ 
        install -m 0644 ${S}/server/__init__.py ${D}/usr/server/ 
        
        # CONFIG
        install -d ${D}/usr/server/config
        install -m 0644 ${S}/server/config/* ${D}/usr/server/config/

        # INTERFACES
        install -d ${D}/usr/server/interfaces
        install -m 0644 ${S}/server/interfaces/__init__.py ${D}/usr/server/interfaces/
        install -d ${D}/usr/server/interfaces/amx_usp_interface
        install -m 0644 ${S}/server/interfaces/amx_usp_interface/* ${D}/usr/server/interfaces/amx_usp_interface/

        # MANAGERS
        install -d ${D}/usr/server/managers
        install -m 0644 ${S}/server/managers/__init__.py ${D}/usr/server/managers/
        install -d ${D}/usr/server/managers/wifi_5GHz_band_manager
        install -m 0644 ${S}/server/managers/wifi_5GHz_band_manager/* ${D}/usr/server/managers/wifi_5GHz_band_manager/

        # REST API
        install -d ${D}/usr/server/rest_api
        install -m 0644 ${S}/server/rest_api/__init__.py ${D}/usr/server/rest_api/
        install -d ${D}/usr/server/rest_api/wifi_controler
        install -m 0644 ${S}/server/rest_api/wifi_controler/* ${D}/usr/server/rest_api/wifi_controler/

        # TEST
        install -d ${D}/usr/tests
        install -m 0644 ${S}/tests/test_usp.py ${D}/usr/tests/
        install -m 0644 ${S}/tests/test_usp_basic.py ${D}/usr/tests/
}

FILES:${PN} += "/usr/server/*"
FILES:${PN} += "/usr/tests/*"