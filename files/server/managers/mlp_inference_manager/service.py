"""MLP inference manager"""

import logging
from typing import Iterable, Tuple
import numpy as np
from datetime import datetime, timedelta
from flask import Flask
from server.interfaces.mlp_interface import MlpModelInterface
from server.common import boxCounters, StationCounters, BoxDataForInferenceInput, StationDataForInferenceInput, SingleStationInferenceResult

logger = logging.getLogger(__name__)

class MlpInferenceManager():
    """Manager for MLP inferences"""

    mlp_model_interface: MlpModelInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the MlpInferenceManager")

            # Initialize MLP model interface
            self.mlp_model_interface = MlpModelInterface(model_path=app.config["MODEL"])


    def perform_inferences(
            self,
            counters_2GHz : boxCounters,
            counters_5GHz : boxCounters,
            counters_stations: Iterable[StationCounters],
            counters_array_min_size: int
        ) -> Tuple[bool, Iterable[SingleStationInferenceResult]]:
        """Perform inferences on counters data"""

        if len(counters_2GHz.rx_Mbps) < counters_array_min_size:
            logger.info("Counters are not filled yet")
            return True, []

        # If 5GHz band is OFF, counter is None
        if counters_5GHz is None:
            # Use only 2.4GHz counter values
            rx_Mbps_array = counters_2GHz.rx_Mbps
            tx_Mbps_array = counters_2GHz.tx_Mbps
            noise = counters_2GHz.noise
            rx_pps = counters_2GHz.rx_pps
            tx_pps = counters_2GHz.tx_pps
            load = counters_2GHz.load
            freeTime = 100 - load
            rxTime = counters_2GHz.rxTime
            vendorStats_glitch = counters_2GHz.vendorStats_glitch
            obssTime = counters_2GHz.obssTime
            txTime = counters_2GHz.txTime
            intTime = counters_2GHz.intTime
            noise_air = counters_2GHz.noise_air
            tx_err_ps = counters_2GHz.tx_err_ps
            tx_ber = counters_2GHz.tx_ber

        else:
            # Compute inference box counter values from 2.4GH and 5GHz
            FACTOR = 2.5
            rx_Mbps_array = [a + b for a, b in zip(counters_2GHz.rx_Mbps, counters_5GHz.rx_Mbps)]
            tx_Mbps_array = [a + b for a, b in zip(counters_2GHz.tx_Mbps, counters_5GHz.tx_Mbps)]
            noise = [min(a, b) for a, b in zip(counters_2GHz.noise, counters_5GHz.noise)]
            rx_pps = counters_2GHz.rx_pps + counters_2GHz.tx_pps
            tx_pps = counters_2GHz.tx_pps + counters_2GHz.tx_pps
            load = counters_2GHz.load + (FACTOR * counters_5GHz.load)
            freeTime = 100 - load
            rxTime = counters_2GHz.rxTime + (FACTOR * counters_5GHz.rxTime)
            vendorStats_glitch = counters_2GHz.vendorStats_glitch + counters_5GHz.vendorStats_glitch
            obssTime = counters_2GHz.obssTime + counters_5GHz.obssTime
            txTime = counters_2GHz.txTime + (FACTOR * counters_5GHz.txTime)
            intTime = counters_2GHz.intTime + counters_5GHz.intTime
            noise_air = min(counters_2GHz.noise_air, counters_5GHz.noise_air)
            tx_err_ps = counters_2GHz.tx_err_ps + counters_5GHz.tx_err_ps
            tx_ber = counters_2GHz.tx_ber + counters_5GHz.tx_ber

        logger.error(
            f"\nCOUNTERS FOR INFERENCE: "
            f"rx_Mbps_array:{rx_Mbps_array}  tx_Mbps_array:{tx_Mbps_array}  "
            f"noise:{noise}  "
            f"rx_pps:{rx_pps}  tx_pps:{tx_pps}  "
            f"load:{load}  "
            f"freeTime:{freeTime}  "
            f"rxTime:{rxTime}  "
            f"txTime:{txTime}  "
            f"obssTime:{obssTime}  "
            f"intTime:{intTime}  "
            f"vendorStats_glitch:{vendorStats_glitch}  "
            f"noise_air:{noise_air}  "
            f"tx_err_ps:{tx_err_ps}  "
            f"tx_ber:{tx_ber}\n"
        )

        try:
            box_data_for_inference = BoxDataForInferenceInput(
                rx_Mbps = rx_Mbps_array[-1],
                rx_Mbps_lag1 = rx_Mbps_array[-2],
                rx_Mbps_lag2 = rx_Mbps_array[-3],
                rx_Mbps_lag3 = rx_Mbps_array[-4],
                rx_Mbps_avg3 = np.mean(rx_Mbps_array[-3:]),
                rx_Mbps_avg5 = np.mean(rx_Mbps_array[-5:]),
                rx_Mbps_avg7 = np.mean(rx_Mbps_array[-7:]),
                tx_Mbps = tx_Mbps_array[-1],
                tx_Mbps_lag1 = tx_Mbps_array[-2],
                tx_Mbps_lag2 = tx_Mbps_array[-3],
                tx_Mbps_lag3 = tx_Mbps_array[-4],
                tx_Mbps_avg3 = np.mean(tx_Mbps_array[-3:]),
                tx_Mbps_avg5 = np.mean(tx_Mbps_array[-5:]),
                tx_Mbps_avg7 = np.mean(tx_Mbps_array[-7:]),
                noise = noise[-1],
                noise_lag3 = noise[-4],
                noise_avg3 = np.mean(noise[-3:]),
                noise_avg5 = np.mean(noise[-5:]),
                noise_avg7 = np.mean(noise[-7:]),
                rx_pps = rx_pps,
                tx_pps = tx_pps,
                load = load,
                freeTime = freeTime,
                rxTime = rxTime,
                vendorStats_glitch = vendorStats_glitch,
                obssTime = obssTime,
                txTime = txTime,
                intTime = intTime,
                noise_air = noise_air,
                tx_err_ps = tx_err_ps,
                tx_ber = tx_ber,
            )
        except:
            logger.error("Error when retreiving station counters to perform inference")
            return False, []

        stations_data_for_inference = []
        # Loop over the counters stations dict
        for station in counters_stations:
            # Check that counters are already filled
            if len(counters_stations[station].rx_Mbps) < counters_array_min_size:
                continue
            # Compute station values
            try:
                stations_data_for_inference.append(
                    StationDataForInferenceInput(
                        station=station,
                        rx_Mbps = counters_stations[station].rx_Mbps[-1],
                        rx_Mbps_lag1 = counters_stations[station].rx_Mbps[-2],
                        rx_Mbps_lag2 = counters_stations[station].rx_Mbps[-3],
                        rx_Mbps_lag3 = counters_stations[station].rx_Mbps[-4],
                        rx_Mbps_lag5 = counters_stations[station].rx_Mbps[-6],
                        rx_Mbps_lag7 = counters_stations[station].rx_Mbps[-8],
                        rx_Mbps_avg3 = np.mean(counters_stations[station].rx_Mbps[-3:]),
                        rx_Mbps_avg5 = np.mean(counters_stations[station].rx_Mbps[-5:]),
                        rx_Mbps_avg7 = np.mean(counters_stations[station].rx_Mbps[-7:]),
                        rx_Mbps_avg10 = np.mean(counters_stations[station].rx_Mbps),
                        tx_Mbps = counters_stations[station].tx_Mbps[-1],
                        tx_Mbps_lag1 = counters_stations[station].tx_Mbps[-2],
                        tx_Mbps_avg3 = np.mean(counters_stations[station].tx_Mbps[-3:]),
                        tx_Mbps_avg5 = np.mean(counters_stations[station].tx_Mbps[-5:]),
                        signalStrength = counters_stations[station].signalStrength[-1],
                        signalStrength_lag1 = counters_stations[station].signalStrength[-2],
                        signalStrength_lag2 = counters_stations[station].signalStrength[-3],
                        signalStrength_lag3 = counters_stations[station].signalStrength[-4],
                        signalStrength_lag5 = counters_stations[station].signalStrength[-6],
                        signalStrength_lag7 = counters_stations[station].signalStrength[-8],
                        signalStrength_avg3 = np.mean(counters_stations[station].signalStrength[-3:]),
                        signalStrength_avg5 = np.mean(counters_stations[station].signalStrength[-5:]),
                        signalStrength_avg7 = np.mean(counters_stations[station].signalStrength[-7:]),
                        signalStrength_avg10 = np.mean(counters_stations[station].signalStrength[-10:]),
                        rx_pps = counters_stations[station].rx_pps,
                        tx_pps = counters_stations[station].tx_pps,
                        uplinkMCS = counters_stations[station].uplinkMCS,
                        lastDataUplinkRate = counters_stations[station].lastDataUplinkRate,
                        lastDataDownlinkRate = counters_stations[station].lastDataDownlinkRate,
                        uplinkShortGuard = counters_stations[station].uplinkShortGuard,
                        downlinkMCS = counters_stations[station].downlinkMCS,
                        avgSignalStrengthByChain = counters_stations[station].avgSignalStrengthByChain,
                        signalNoiseRatio = counters_stations[station].signalNoiseRatio,
                    )
                )
            except:
                logger.error("Error when retreiving station counters to perform inference")
                return False, []
        inference_results = self.mlp_model_interface.perform_inference(
            box_data=box_data_for_inference,
            stations_data=stations_data_for_inference,
        )
        if not inference_results:
            logger.error("Error when performing inferences")
            return False, []

        return True, inference_results

    def get_valid_inferences(self, counters_stations: Iterable[StationCounters]) -> Iterable[SingleStationInferenceResult]:
        now = datetime.now()
        valid_inferences=[]
        for station in counters_stations:
            if len(counters_stations[station].inferences_results) > 0:
                # Old counters filter
                if now - counters_stations[station].last_sample_timestamp < timedelta(seconds=2):
                    # Append inference result
                    valid_inferences.append(counters_stations[station].inferences_results[-1])
        return valid_inferences


mlp_inference_manager_service: MlpInferenceManager = MlpInferenceManager()
""" MLP manager service singleton"""
