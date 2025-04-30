"""Box wifi counters common """

from datetime import datetime
from server.common import boxCounters, boxStatsSample, stationStatsSample, StationCounters

BANDS = ["2.4GHz", "5GHz", "6GHz"]
MAX_THROUGHPUT_COUNTER_VALUE = 120
COUNTERS_ARRAY_SIZE_TO_PERFORM_INFERENCE = 6

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
        tx_err_pps = None,
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
            inactive=sample.inactive,
            avgSignalStrengthByChain = sample.avgSignalStrengthByChain,
            signalNoiseRatio = sample.avgSignalStrengthByChain,
            last_txErrors = sample.txErrors, # Doble check creation avec Gilles
            tx_err_pps = None ,
            tx_ber = None,
            band= None,
            inferences_results = [],
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
