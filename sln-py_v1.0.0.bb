FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://server"
SRC_URI += "file://tests"
SRC_URI += "file://test_models"
SRC_URI += "file://models"

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

        ### COMMON
        install -d ${D}/usr/server/common
        install -m 0644 ${S}/server/common/__init__.py ${D}/usr/server/common/
        install -m 0644 ${S}/server/common/model.py ${D}/usr/server/common/
        install -d ${D}/usr/server/common/exception
        install -m 0644 ${S}/server/common/exception/* ${D}/usr/server/common/exception/

        # INTERFACES
        install -d ${D}/usr/server/interfaces
        install -m 0644 ${S}/server/interfaces/__init__.py ${D}/usr/server/interfaces/
        # amx_usp_interface
        install -d ${D}/usr/server/interfaces/amx_usp_interface
        install -m 0644 ${S}/server/interfaces/amx_usp_interface/* ${D}/usr/server/interfaces/amx_usp_interface/
        # mlp_interface
        install -d ${D}/usr/server/interfaces/mlp_interface
        install -m 0644 ${S}/server/interfaces/mlp_interface/* ${D}/usr/server/interfaces/mlp_interface/

        # MANAGERS
        install -d ${D}/usr/server/managers
        install -m 0644 ${S}/server/managers/__init__.py ${D}/usr/server/managers/
        # wifi_bands_manager
        install -d ${D}/usr/server/managers/wifi_5GHz_band_manager
        install -m 0644 ${S}/server/managers/wifi_5GHz_band_manager/* ${D}/usr/server/managers/wifi_5GHz_band_manager/
        # box_counters_manager
        install -d ${D}/usr/server/managers/box_counters_manager
        install -m 0644 ${S}/server/managers/box_counters_manager/* ${D}/usr/server/managers/box_counters_manager/
        # mlp_inference_manager
        install -d ${D}/usr/server/managers/mlp_inference_manager
        install -m 0644 ${S}/server/managers/mlp_inference_manager/* ${D}/usr/server/managers/mlp_inference_manager/

        # NOTIFICATION
        install -d ${D}/usr/server/notification
        install -m 0644 ${S}/server/notification/__init__.py ${D}/usr/server/notification/
        install -m 0644 ${S}/server/notification/service.py ${D}/usr/server/notification/

        # REST API
        install -d ${D}/usr/server/rest_api
        install -m 0644 ${S}/server/rest_api/__init__.py ${D}/usr/server/rest_api/
        # common
        install -d ${D}/usr/server/rest_api/common
        install -m 0644 ${S}/server/rest_api/common/* ${D}/usr/server/rest_api/common/
        # wifi_controller
        install -d ${D}/usr/server/rest_api/wifi_controller
        install -m 0644 ${S}/server/rest_api/wifi_controller/* ${D}/usr/server/rest_api/wifi_controller/

        # TEST
        install -d ${D}/usr/tests
        install -m 0644 ${S}/tests/test_usp.py ${D}/usr/tests/
        install -m 0644 ${S}/tests/test_usp_basic.py ${D}/usr/tests/

        # MODELS
        install -d ${D}/usr/models
        install -d ${D}/usr/models/LGBM_C
        install -d ${D}/usr/models/MLP_C
        install -d ${D}/usr/models/XGBoost_C
        install -m 0644 ${S}/models/LGBM_C/* ${D}/usr/models/LGBM_C/
        install -m 0644 ${S}/models/MLP_C/* ${D}/usr/models/MLP_C/
        install -m 0644 ${S}/models/XGBoost_C/* ${D}/usr/models/XGBoost_C/

        # TEST MODELS
        install -d ${D}/usr/test_models
        install -d ${D}/usr/test_models/expected_results
        install -d ${D}/usr/test_models/expected_results/LGBM_C
        install -d ${D}/usr/test_models/expected_results/MLP_C
        install -d ${D}/usr/test_models/expected_results/XGBoost_C
        install -m 0644 ${S}/test_models/test_models.sh ${D}/usr/test_models/
        install -m 0644 ${S}/test_models/compare_results.py ${D}/usr/test_models/
        install -m 0644 ${S}/test_models/test_model.py ${D}/usr/test_models/
        install -m 0644 ${S}/test_models/expected_results/LGBM_C/* ${D}/usr/test_models/expected_results/LGBM_C/
        install -m 0644 ${S}/test_models/expected_results/MLP_C/* ${D}/usr/test_models/expected_results/MLP_C/
        install -m 0644 ${S}/test_models/expected_results/XGBoost_C/* ${D}/usr/test_models/expected_results/XGBoost_C/
}

FILES:${PN} += "/usr/server/*"
FILES:${PN} += "/usr/tests/*"
FILES:${PN} += "/usr/test_models/*"
FILES:${PN} += "/usr/models/*"
