"""Box counters data manager"""

import logging
from datetime import datetime, timedelta
from typing import Iterable
from server.common import boxCounters, boxStatsSample, stationStatsSample, SingleStationInferenceResult
from .common import create_box_counter, create_stations_counter, convert_incremental_values_in_instantaneous_values, convert_bytes_per_sec_into_Mbps
from .common import BANDS, MAX_THROUGHPUT_COUNTER_VALUE, COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE

logger = logging.getLogger(__name__)


class Counters():
    """Box counters class"""

    purge_counters_timer_in_secs: int
    counters_5GHz: boxCounters
    counters_2GHz: boxCounters
    counters_stations: dict

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

    def update_box_counter(self, band: str, sample: boxStatsSample) -> bool:
        """Update box counters from sample"""
        # Health check
        if band not in BANDS:
            logger.error(f"Impossible to update counters, band {band} doesnt exist")
            return False
        if band == "5GHz":
            counter_to_update = self.counters_5GHz
            # If 5GHz band is OFF sample is None
            if sample is None:
                self.counters_5GHz = None
                logger.error(f"5GHz band is OFF counter is set to None")
                return True

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

    def append_inference_results_to_counters(self, inference_results: Iterable[SingleStationInferenceResult]):
        """Append inference results to class counters"""
        for result in inference_results:
            if result.station in self.counters_stations:
                if len(self.counters_stations[result.station].inferences_results) < COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE:
                    self.counters_stations[result.station].inferences_results.append(result)
                else:
                    self.counters_stations[result.station].inferences_results = self.counters_stations[result.station].inferences_results[1:] + [result]


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
                f"tx_Mbps:{self.counters_2GHz.tx_Mbps}  rx_Mbps:{self.counters_2GHz.rx_Mbps}  "
                f"noise:{self.counters_2GHz.noise}  "
                f"tx_pps:{self.counters_2GHz.tx_pps}  rx_pps:{self.counters_2GHz.rx_pps}  "
                f"load:{self.counters_2GHz.load}  "
                f"freeTime:{self.counters_2GHz.freeTime}  "
                f"rxTime:{self.counters_2GHz.rxTime}  "
                f"obssTime:{self.counters_2GHz.obssTime}  "
                f"intTime:{self.counters_2GHz.intTime}  "
                f"vendorStats_glitch:{self.counters_2GHz.vendorStats_glitch}  "
                f"tx_err_ps:{self.counters_2GHz.tx_err_ps}  "
                f"tx_ber:{self.counters_2GHz.tx_ber}\n"
            )
            if self.counters_5GHz is None:
                logger.error(f"BOX COUNTERS 5GHz - : None, band is OFF")
            else:
                logger.error(
                    f"\nBOX COUNTERS 5GHz - "
                    f"tx_Mbps:{self.counters_5GHz.tx_Mbps}  rx_Mbps:{self.counters_5GHz.rx_Mbps}"
                    f"noise:{self.counters_5GHz.noise}  "
                    f"tx_pps:{self.counters_5GHz.tx_pps}  rx_pps:{self.counters_5GHz.rx_pps}  "
                    f"load:{self.counters_5GHz.load}  "
                    f"freeTime:{self.counters_5GHz.freeTime}  "
                    f"rxTime:{self.counters_5GHz.rxTime}  "
                    f"obssTime:{self.counters_5GHz.obssTime}  "
                    f"intTime:{self.counters_5GHz.intTime}  "
                    f"vendorStats_glitch:{self.counters_5GHz.vendorStats_glitch}  "
                    f"tx_err_ps:{self.counters_5GHz.tx_err_ps}  "
                    f"tx_ber:{self.counters_5GHz.tx_ber}\n"
                )
        if print_stations_counters:
            # STATIONS COUNTERS
            if len(self.counters_stations) > 0:
                logger.error("\nSTATIONS COUNTERS:")
                logger.error(
                    ' '.join(
                        f"\n{station}: "
                        f"tx_Mbps:{self.counters_stations[station].tx_Mbps}  "
                        f"rx_Mbps:{self.counters_stations[station].rx_Mbps}  "
                        f"SignalStrength:{self.counters_stations[station].signalStrength}  "
                        f"rx_pps:{self.counters_stations[station].rx_pps}  "
                        f"tx_pps:{self.counters_stations[station].tx_pps}  "
                        f"uplinkMCS:{self.counters_stations[station].uplinkMCS}  "
                        f"lastDataUplinkRate:{self.counters_stations[station].lastDataUplinkRate}  "
                        f"lastDataDownlinkRate:{self.counters_stations[station].lastDataDownlinkRate}  "
                        f"uplinkShortGuard:{self.counters_stations[station].uplinkShortGuard}  "
                        f"downlinkMCS:{self.counters_stations[station].downlinkMCS}  "
                        f"avgSignalStrengthByChain:{self.counters_stations[station].avgSignalStrengthByChain}  "
                        f"signalNoiseRatio:{self.counters_stations[station].signalNoiseRatio}  "
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
