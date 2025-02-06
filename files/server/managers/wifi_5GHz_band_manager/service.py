"""Wifi Bands manager"""

import logging
import threading
import queue
import numpy as np
from datetime import datetime, timedelta
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.interfaces.mlp_interface import MlpModelInterface
from server.common import samples_queue, boxCounters, boxStatsSample, stationStatsSample, StationCounters, BoxDataForInferenceInput, StationDataForInferenceInput

logger = logging.getLogger(__name__)

BANDS = ["2.4GHz", "5GHz", "6GHz"]
MAX_THROUGHPUT_COUNTER_VALUE = 40
COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE = 10

class WifiBandsManager(threading.Thread):
    """Manager for wifi control"""

    amx_usp_interface: AmxUspInterface
    mlp_model_interface: MlpModelInterface
    purge_counters_timer_in_secs: int
    counters_5GHz: boxCounters
    counters_2GHz: boxCounters
    counters_stations: dict

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the WifiBandsManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()

            # Initialize MLP model interface
            self.mlp_model_interface = MlpModelInterface(model_path=app.config["MODEL"])

            # Initialize counters
            self.purge_counters_timer_in_secs = app.config["COUNTERS"]["PURGE_TIMER_IN_SECS"]
            self.init_counters()

            # Run CountWifi bands inferences in dedicated thread
            super(WifiBandsManager, self).__init__(name="WifiBandsInferencesThread")
            self.setDaemon(True)
            logger.info("Running wifi bands manager inferences loop in dedicated thread")
            self.start()

    def init_counters(self):
        """Initialize service counters"""
        self.counters_5GHz = boxCounters(
                last_sample_timestamp = None,
                rx_Mbps = [],
                last_bytesReceived = None,
                rx_pps = None,
                last_packetsReceived = None,
                tx_Mbps = [],
                last_bytesSent = None,
                tx_pps= None,
                last_packetsSent = None,
                noise = [],
                load = None,
                freeTime = None,
                rxTime = None,
                vendorStats_glitch = None,
                obssTime = None,
                txTime = None,
                intTime = None,
                noise_air = None,
                last_errorsReceived = None,
                last_errorsSent = None,
                tx_err_ps = None,
                tx_ber = None,
            )
        self.counters_2GHz = boxCounters(
            last_sample_timestamp = None,
            rx_Mbps = [],
            last_bytesReceived = None,
            rx_pps = None,
            last_packetsReceived = None,
            tx_Mbps = [],
            last_bytesSent = None,
            tx_pps= None,
            last_packetsSent = None,
            noise = [],
            load = None,
            freeTime = None,
            rxTime = None,
            vendorStats_glitch = None,
            obssTime = None,
            txTime = None,
            intTime = None,
            noise_air = None,
            last_errorsReceived = None,
            last_errorsSent = None,
            tx_err_ps = None,
            tx_ber = None,
        )
        self.counters_stations = {}

    def run(self):
        """Run thread"""
        while True:
            try:
                sample = samples_queue.get(timeout=0.3)
            except queue.Empty:
                sample = None
            if sample is not None:  # Counters sample waitting in queue
                try:
                    sample_5GHz = sample["box_counters"]["5GHz"]
                    sample_2GHz = sample["box_counters"]["2.4GHz"]
                    sample_stations = sample["stations_counters"]
                except:
                    logger.error("Error unpacking sample")
                    self.init_counters()
                    continue
                # Update box counters
                if not self.update_box_counter(band="5GHz", sample=sample_5GHz):
                    logger.error("Error in box counters update for 5GHz, counters are reset")
                    self.init_counters()
                    continue
                if not self.update_box_counter(band="2.4GHz", sample=sample_2GHz):
                    logger.error("Error in box counters update for 2.4GHz, counters are reset")
                    self.init_counters()
                    continue
                # Update stations counters
                if not self.update_stations_counters(sample=sample_stations):
                    logger.error("Error in stations counters update, counters are reset")
                    self.init_counters()
                    continue

                # Purge disconnected stations from counters
                if not self.purge_stations_counters():
                    logger.error("Error in stations counters purge, counters are reset")
                    self.init_counters()
                    continue

                # Perform inferences
                if not self.perform_inferences():
                    logger.error("Error when performing inferences, counters are reset")
                    self.init_counters()
                    continue

                # Print counters for debug
                self.print_counters()
                # TODO: evaluate band status change

    def perform_inferences(self) -> bool:
        """Perform inferences on counters data"""

        if len(self.counters_2GHz.rx_Mbps) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
            logger.info("Counters are not filled yet")
            return True
        FACTOR = 2.5
        # Compute inference box counter values
        rx_Mbps_array = [a + b for a, b in zip(self.counters_2GHz.rx_Mbps, self.counters_5GHz.rx_Mbps)]
        tx_Mbps_array = [a + b for a, b in zip(self.counters_2GHz.tx_Mbps, self.counters_5GHz.tx_Mbps)]
        noise = [min(a, b) for a, b in zip(self.counters_2GHz.noise, self.counters_5GHz.noise)]
        rx_pps = self.counters_2GHz.rx_pps + self.counters_2GHz.tx_pps
        tx_pps = self.counters_2GHz.tx_pps + self.counters_2GHz.tx_pps
        load = self.counters_2GHz.load + (FACTOR * self.counters_5GHz.load)
        freeTime = 100 - load
        rxTime = self.counters_2GHz.rxTime + (FACTOR * self.counters_5GHz.rxTime)
        vendorStats_glitch = self.counters_2GHz.vendorStats_glitch + self.counters_5GHz.vendorStats_glitch
        obssTime = self.counters_2GHz.obssTime + self.counters_5GHz.obssTime
        txTime = self.counters_2GHz.txTime + (FACTOR * self.counters_5GHz.txTime)
        intTime = self.counters_2GHz.intTime + self.counters_5GHz.intTime
        noise_air = min(self.counters_2GHz.noise_air, self.counters_5GHz.noise_air)
        tx_err_ps = self.counters_2GHz.tx_err_ps + self.counters_5GHz.tx_err_ps
        tx_ber = self.counters_2GHz.tx_ber + self.counters_5GHz.tx_ber

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
            return False

        stations_data_for_inference = []
        # Loop over the counters stations dict
        for station in self.counters_stations:
            # Check that counters are already filled
            if len(self.counters_stations[station].rx_Mbps) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
                continue
            # Compute station values
            try:
                stations_data_for_inference.append(
                    StationDataForInferenceInput(
                        station=station,
                        rx_Mbps = self.counters_stations[station].rx_Mbps[-1],
                        rx_Mbps_lag1 = self.counters_stations[station].rx_Mbps[-2],
                        rx_Mbps_lag2 = self.counters_stations[station].rx_Mbps[-3],
                        rx_Mbps_lag3 = self.counters_stations[station].rx_Mbps[-4],
                        rx_Mbps_lag5 = self.counters_stations[station].rx_Mbps[-6],
                        rx_Mbps_lag7 = self.counters_stations[station].rx_Mbps[-8],
                        rx_Mbps_avg3 = np.mean(self.counters_stations[station].rx_Mbps[-3:]),
                        rx_Mbps_avg5 = np.mean(self.counters_stations[station].rx_Mbps[-5:]),
                        rx_Mbps_avg7 = np.mean(self.counters_stations[station].rx_Mbps[-7:]),
                        rx_Mbps_avg10 = np.mean(self.counters_stations[station].rx_Mbps),
                        tx_Mbps = self.counters_stations[station].tx_Mbps[-1],
                        tx_Mbps_lag1 = self.counters_stations[station].tx_Mbps[-2],
                        tx_Mbps_avg3 = np.mean(self.counters_stations[station].tx_Mbps[-3:]),
                        tx_Mbps_avg5 = np.mean(self.counters_stations[station].tx_Mbps[-5:]),
                        signalStrength = self.counters_stations[station].signalStrength[-1],
                        signalStrength_lag1 = self.counters_stations[station].signalStrength[-2],
                        signalStrength_lag2 = self.counters_stations[station].signalStrength[-3],
                        signalStrength_lag3 = self.counters_stations[station].signalStrength[-4],
                        signalStrength_lag5 = self.counters_stations[station].signalStrength[-6],
                        signalStrength_lag7 = self.counters_stations[station].signalStrength[-8],
                        signalStrength_avg3 = np.mean(self.counters_stations[station].signalStrength[-3:]),
                        signalStrength_avg5 = np.mean(self.counters_stations[station].signalStrength[-5:]),
                        signalStrength_avg7 = np.mean(self.counters_stations[station].signalStrength[-7:]),
                        signalStrength_avg10 = np.mean(self.counters_stations[station].signalStrength[-10:]),
                        rx_pps = self.counters_stations[station].rx_pps,
                        tx_pps = self.counters_stations[station].tx_pps,
                        uplinkMCS = self.counters_stations[station].uplinkMCS,
                        lastDataUplinkRate = self.counters_stations[station].lastDataUplinkRate,
                        lastDataDownlinkRate = self.counters_stations[station].lastDataDownlinkRate,
                        uplinkShortGuard = self.counters_stations[station].uplinkShortGuard,
                        downlinkMCS = self.counters_stations[station].downlinkMCS,
                        avgSignalStrengthByChain = self.counters_stations[station].avgSignalStrengthByChain,
                        signalNoiseRatio = self.counters_stations[station].signalNoiseRatio,
                    )
                )
            except:
                logger.error("Error when retreiving station counters to perform inference")
                return False
        inference_results = self.mlp_model_interface.perform_inference(
            box_data=box_data_for_inference,
            stations_data=stations_data_for_inference,
        )
        if not inference_results:
            logger.error("Error when performing inferences")
            return False

        # Append results to stations counters
        for result in inference_results:
            if result.station in self.counters_stations:
                if len(self.counters_stations[result.station].inferences_results) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
                    self.counters_stations[result.station].inferences_results.append(result)
                else:
                    self.counters_stations[result.station].inferences_results = self.counters_stations[result.station].inferences_results[1:] + [result]
        return True

    def update_box_counter(self, band: str, sample: boxStatsSample) -> bool:
        """Update box counters from sample"""
        # Health check
        if band not in BANDS:
            logger.error(f"Impossible to update counters, band {band} doesnt exist")
            return False
        if band == "5GHz":
            counter_to_update = self.counters_5GHz
        elif band == "2.4GHz":
            counter_to_update = self.counters_2GHz
        else:
            logger.error(f"Impossible to update counters, service not available for band {band}")
            return False

        reset_counter = False
        # Check if is first received sample
        if counter_to_update.last_sample_timestamp is None:
            logger.debug(f"First sample received for band {band}")
            reset_counter = True
        else:
            # Check if last sample received is too old
            secs_since_last_sample = (sample.timestamp -counter_to_update.last_sample_timestamp).total_seconds()
            logger.debug(f"Time elapsed since last sample: {secs_since_last_sample}")
            if secs_since_last_sample > self.purge_counters_timer_in_secs or secs_since_last_sample < 0:
                reset_counter = True

        if reset_counter:
            logger.debug(f"Reset counter")
            # Reset the counter
            counter_to_update = create_box_counter(sample)
        else:
            # Update counter values
            # Get rx_Mbps
            _rx_Bps = convert_incremental_values_in_instantaneous_values(
                timestamp_1=counter_to_update.last_sample_timestamp,
                timestamp_2=sample.timestamp,
                value_1=counter_to_update.last_bytesReceived,
                value_2=sample.bytesReceived,
                power_level=32,
            )
            new_rx_Mbps = convert_bytes_per_sec_into_Mbps(value_in_Bps=_rx_Bps)
            if new_rx_Mbps > MAX_THROUGHPUT_COUNTER_VALUE:
                new_rx_Mbps=MAX_THROUGHPUT_COUNTER_VALUE
            # Get tx_Mbps
            _tx_Bps = convert_incremental_values_in_instantaneous_values(
                timestamp_1=counter_to_update.last_sample_timestamp,
                timestamp_2=sample.timestamp,
                value_1=counter_to_update.last_bytesSent,
                value_2=sample.bytesSent,
                power_level=32,
            )
            new_tx_Mbps = convert_bytes_per_sec_into_Mbps(value_in_Bps=_tx_Bps)
            if new_tx_Mbps > MAX_THROUGHPUT_COUNTER_VALUE:
                new_tx_Mbps=MAX_THROUGHPUT_COUNTER_VALUE
            # Get rx_pps
            new_rx_pps = convert_incremental_values_in_instantaneous_values(
                timestamp_1=counter_to_update.last_sample_timestamp,
                timestamp_2=sample.timestamp,
                value_1=counter_to_update.last_packetsReceived,
                value_2=sample.packetsReceived,
                power_level=32,
            )

            # Get tx_pps
            new_tx_pps = convert_incremental_values_in_instantaneous_values(
                timestamp_1=counter_to_update.last_sample_timestamp,
                timestamp_2=sample.timestamp,
                value_1=counter_to_update.last_packetsSent,
                value_2=sample.packetsSent,
                power_level=32,
            )

            # Get tx_err_ps
            new_tx_err_ps = convert_incremental_values_in_instantaneous_values(
                timestamp_1=counter_to_update.last_sample_timestamp,
                timestamp_2=sample.timestamp,
                value_1=counter_to_update.last_errorsSent,
                value_2=sample.errorsSent,
                power_level=32,
            )

            # Get tx_ber
            if new_tx_Mbps != 0:
                new_tx_ber = new_tx_err_ps / (new_tx_Mbps * 1E6)
            else:
                new_tx_ber = 0

            # Update counters arrays values
            if len(counter_to_update.rx_Mbps) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
                # Arrays not completely filled
                counter_to_update.rx_Mbps.append(new_rx_Mbps)
                counter_to_update.tx_Mbps.append(new_tx_Mbps)
                counter_to_update.noise.append(sample.noise)
            else:
                # arrays are already fully filled
                counter_to_update.rx_Mbps = counter_to_update.rx_Mbps[1:] + [new_rx_Mbps]
                counter_to_update.tx_Mbps = counter_to_update.tx_Mbps[1:] + [new_tx_Mbps]
                counter_to_update.noise = counter_to_update.noise[1:] + [sample.noise]

            # Update counters values
            counter_to_update.last_sample_timestamp = sample.timestamp
            counter_to_update.last_bytesReceived = sample.bytesReceived
            counter_to_update.rx_pps = new_rx_pps
            counter_to_update.last_packetsReceived = sample.packetsReceived
            counter_to_update.last_bytesSent = sample.bytesSent
            counter_to_update.tx_pps = new_tx_pps
            counter_to_update.last_packetsSent=sample.packetsSent
            counter_to_update.load=sample.load
            counter_to_update.freeTime=sample.freeTime
            counter_to_update.rxTime=sample.rxTime
            counter_to_update.vendorStats_glitch=sample.vendorStats_glitch
            counter_to_update.obssTime=sample.obssTime
            counter_to_update.txTime=sample.txTime
            counter_to_update.intTime=sample.intTime
            counter_to_update.noise_air=sample.noise_air
            counter_to_update.last_errorsReceived=sample.errorsReceived
            counter_to_update.last_errorsSent=sample.errorsSent
            counter_to_update.tx_err_ps=new_tx_err_ps
            counter_to_update.tx_ber=new_tx_ber

        # Reasign counters to instance
        if band == "5GHz":
            self.counters_5GHz =counter_to_update
        elif band == "2.4GHz":
            self.counters_2GHz = counter_to_update
        return True

    def update_stations_counters(self, sample: stationStatsSample) -> bool:
        """Update stations counters from sample"""
        updated_counters = {}
        for station in sample:
            # Check if a counter already exists for station
            if station not in self.counters_stations:
                # Create a new counter
                updated_counters[station] = create_stations_counter(station, sample[station])
                continue
            else:
                # The counter already exists
                counter_to_update = self.counters_stations[station]

                # Check if last sample received for counter is too old
                secs_since_last_sample = (sample[station].timestamp - counter_to_update.last_sample_timestamp).total_seconds()
                logger.debug(f"Time elapsed since last sample: {secs_since_last_sample}")
                if secs_since_last_sample > self.purge_counters_timer_in_secs or secs_since_last_sample < 0:
                    # Reset the counter
                    updated_counters[station] = create_stations_counter(station, sample[station])
                    continue

                # Update counter values
                # Get tx_Mbps
                _tx_Bps = convert_incremental_values_in_instantaneous_values(
                    timestamp_1=counter_to_update.last_sample_timestamp,
                    timestamp_2=sample[station].timestamp,
                    value_1=counter_to_update.last_txBytes,
                    value_2=sample[station].txBytes,
                    power_level=32,
                )
                new_tx_Mbps = convert_bytes_per_sec_into_Mbps(value_in_Bps=_tx_Bps)
                if new_tx_Mbps > MAX_THROUGHPUT_COUNTER_VALUE:
                    new_tx_Mbps = MAX_THROUGHPUT_COUNTER_VALUE

                # Get rx_Mbps
                _rx_Bps = convert_incremental_values_in_instantaneous_values(
                    timestamp_1=counter_to_update.last_sample_timestamp,
                    timestamp_2=sample[station].timestamp,
                    value_1=counter_to_update.last_rxBytes,
                    value_2=sample[station].rxBytes,
                    power_level=32,
                )
                new_rx_Mbps = convert_bytes_per_sec_into_Mbps(value_in_Bps=_rx_Bps)
                if new_rx_Mbps > MAX_THROUGHPUT_COUNTER_VALUE:
                    new_rx_Mbps = MAX_THROUGHPUT_COUNTER_VALUE

                # Get rx_pps
                new_rx_pps = convert_incremental_values_in_instantaneous_values(
                    timestamp_1=counter_to_update.last_sample_timestamp,
                    timestamp_2=sample[station].timestamp,
                    value_1=counter_to_update.last_rxPacketCount,
                    value_2=sample[station].rxPacketCount,
                    power_level=32,
                )

                # Get tx_pps
                new_tx_pps = convert_incremental_values_in_instantaneous_values(
                    timestamp_1=counter_to_update.last_sample_timestamp,
                    timestamp_2=sample[station].timestamp,
                    value_1=counter_to_update.last_txPacketCount,
                    value_2=sample[station].txPacketCount,
                    power_level=32,
                )

                # Update counters arrays values
                if len(counter_to_update.rx_Mbps) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
                    # Arrays not completely filled
                    counter_to_update.rx_Mbps.append(new_rx_Mbps)
                    counter_to_update.tx_Mbps.append(new_tx_Mbps)
                    counter_to_update.signalStrength.append(sample[station].signalStrength)
                else:
                    # arrays are already fully filled
                    counter_to_update.rx_Mbps = counter_to_update.rx_Mbps[1:] + [new_rx_Mbps]
                    counter_to_update.tx_Mbps = counter_to_update.tx_Mbps[1:] + [new_tx_Mbps]
                    counter_to_update.signalStrength = counter_to_update.signalStrength[1:] + [sample[station].signalStrength]

                # Update counters values
                counter_to_update.last_sample_timestamp = sample[station].timestamp
                counter_to_update.last_txBytes = sample[station].txBytes
                counter_to_update.last_rxBytes = sample[station].rxBytes
                counter_to_update.rx_pps = new_rx_pps
                counter_to_update.last_rxPacketCount = sample[station].rxPacketCount
                counter_to_update.tx_pps = new_tx_pps
                counter_to_update.last_txPacketCount = sample[station].txPacketCount
                counter_to_update.uplinkMCS = sample[station].uplinkMCS
                counter_to_update.lastDataUplinkRate = sample[station].lastDataUplinkRate
                counter_to_update.lastDataDownlinkRate = sample[station].lastDataDownlinkRate
                counter_to_update.uplinkShortGuard = sample[station].uplinkShortGuard
                counter_to_update.downlinkMCS = sample[station].downlinkMCS
                counter_to_update.avgSignalStrengthByChain = sample[station].avgSignalStrengthByChain
                counter_to_update.signalNoiseRatio = sample[station].signalNoiseRatio

                # Append counter to updated counters dict
                updated_counters[station] = counter_to_update

        # Reasign counters to instance
        self.counters_stations = updated_counters
        return True

    def purge_stations_counters(self) -> bool:
        """Purge the disconnected stations"""
        delte_from = datetime.now() - timedelta(seconds=self.purge_counters_timer_in_secs)
        stations_to_delete = []

        try:
            # Loop the counters stations dict to get stations to delete
            for station in self.counters_stations:
                if self.counters_stations[station].last_sample_timestamp < delte_from:
                    stations_to_delete.append(station)

            # Delete the unseen stations
            for station in stations_to_delete:
                del self.counters_stations[station]
        except:
            logger.error("Error in stations counter purge")
            return False

        return True

    def print_counters(
            self,
            print_box_counters: bool = True,
            print_stations_counters: bool = True,
            print_inference_results: bool = True,
        ):
        """Print counters for debug"""
        # BOX COUNTERS
        if print_box_counters:
            logger.error(
                f"\nBOX COUNTERS 2.4GHz - "
                f"tx_Mbps:{self.counters_2GHz.tx_Mbps}  rx_Mbps:{self.counters_2GHz.rx_Mbps}\n"
                f"BOX COUNTERS 5GHz - "
                f"tx_Mbps:{self.counters_5GHz.tx_Mbps}  rx_Mbps:{self.counters_5GHz.rx_Mbps}"
            )
        if print_stations_counters:
            # STATIONS COUNTERS
            if len(self.counters_stations) > 0:
                logger.error("\nSTATIONS COUNTERS:")
                logger.error(
                    ' '.join(
                        f"\n{station}: "
                        f"tx_Mbps:{self.counters_stations[station].tx_Mbps}  "
                        f"rx_Mbps:{self.counters_stations[station].rx_Mbps}"
                        for station in self.counters_stations
                    )
                )
        if print_inference_results:
            # STATIONS COUNTERS
            if len(self.counters_stations) > 0:
                logger.error("\nINFERENCES RESULTS:")
                logger.error(
                    ' '.join(
                        f"\n{station}: "
                        f"inferences_results:[{self.counters_stations[station].inference_result_to_str()}]"
                        for station in self.counters_stations
                    )
                )

    def get_band_status(self):
        """Execute get wifi band status command in the livebox using AMX USP """
        # Check if band number exists
        cmd = "Device.WiFi.Radio.2.Status"
        logger.info(f"Getting wifi status - {cmd}")
        status = self.amx_usp_interface.read_object(path=cmd)
        logger.info(f"status: {status}")
        return status


def create_box_counter(sample: boxStatsSample):
    """Create a new box counter"""
    return boxCounters(
        last_sample_timestamp = sample.timestamp,
        rx_Mbps = [],
        last_bytesReceived = sample.bytesReceived,
        rx_pps = None,
        last_packetsReceived = sample.packetsReceived,
        tx_Mbps = [],
        last_bytesSent = sample.bytesSent,
        tx_pps= None,
        last_packetsSent = sample.packetsSent,
        noise = [],
        load = sample.load,
        freeTime = sample.freeTime,
        rxTime = None,
        vendorStats_glitch = sample.vendorStats_glitch,
        obssTime = sample.obssTime,
        txTime = sample.txTime,
        intTime = sample.intTime,
        noise_air = sample.noise_air,
        last_errorsReceived = sample.errorsReceived,
        last_errorsSent = sample.errorsSent,
        tx_err_ps = None,
        tx_ber = None,
    )

def create_stations_counter(station: str, sample: stationStatsSample):
        """Create a new stations counter"""
        return StationCounters(
            last_sample_timestamp = sample.timestamp,
            mac=station,
            tx_Mbps= [],
            last_txBytes= sample.txBytes,
            rx_Mbps = [],
            last_rxBytes = sample.rxBytes,
            rx_pps = None,
            last_rxPacketCount = sample.rxPacketCount,
            tx_pps = None,
            last_txPacketCount = sample.txPacketCount,
            uplinkMCS = sample.uplinkMCS,
            lastDataUplinkRate = sample.lastDataUplinkRate,
            lastDataDownlinkRate = sample.lastDataDownlinkRate,
            signalStrength = [],
            uplinkShortGuard = sample.uplinkShortGuard,
            downlinkMCS = sample.downlinkMCS,
            avgSignalStrengthByChain = sample.avgSignalStrengthByChain,
            signalNoiseRatio = sample.avgSignalStrengthByChain,
            band= None, # TODO: necessary ?
            inferences_results = [],  # TODO: necessary ?
        )

def convert_incremental_values_in_instantaneous_values(
        timestamp_1: datetime,
        timestamp_2: datetime,
        value_1: int,
        value_2: int,
        power_level= 32,
) -> float:
    """Convert incremental to instantaneous value"""
    # Get time interval
    delta_time = timestamp_2 - timestamp_1

    # Get value interval
    delta_value = value_2 - value_1

    # Rule when the counter exceed 2**32 and comeback to 0.
    if delta_value < 0:
        delta_value = (2**power_level - value_1) + value_2

    # Compute the values per second
    value_per_sec = delta_value / delta_time.total_seconds()

    return value_per_sec

def convert_bytes_per_sec_into_Mbps(value_in_Bps: float):
    """Convert from Bps to Mbps"""
    return round(value_in_Bps *8/1e6, 4)


wifi_5GHz_band_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
