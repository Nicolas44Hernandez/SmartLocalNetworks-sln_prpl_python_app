"""Data model for 5GHz band on/off manager package"""

import queue
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


samples_queue = queue.Queue()

@dataclass
class boxStatsSample:
    timestamp: datetime
    bytesReceived: int
    bytesSent: int
    noise: int
    load: int
    freeTime: int
    rxTime: int
    vendorStats_glitch: int
    obssTime: int
    txTime: int
    intTime: int
    noise_air: int   # Is the same as the one retreived in getRadioStats() ?
    packetsReceived: int # pps
    packetsSent: int  # pps
    errorsReceived: int # tx_ber / tx_err_ps
    errorsSent: int # tx_ber / tx_err_ps

@dataclass
class stationStatsSample:
    timestamp: datetime
    txBytes: int
    rxBytes: int
    uplinkMCS: int
    lastDataUplinkRate: int
    lastDataDownlinkRate: int
    signalStrength: int
    avgSignalStrengthByChain: int
    uplinkShortGuard: int
    downlinkMCS: int
    signalNoiseRatio: int
    rxPacketCount: int # pps
    txPacketCount: int # pps


@dataclass
class boxCounters:
    """Model for wifi box counters"""
    last_sample_timestamp: datetime
    rx_Mbps: Iterable[float]
    last_bytesReceived: int
    rx_pps: float
    last_packetsReceived: int
    tx_Mbps: Iterable[float]
    last_bytesSent: int
    tx_pps: float
    last_packetsSent: int
    noise: Iterable[float]
    load: int
    freeTime: int
    rxTime: int
    vendorStats_glitch: int
    obssTime: int
    txTime: int
    intTime: int
    noise_air: int
    last_errorsReceived: int
    last_errorsSent: int
    tx_err_ps: float
    tx_ber: float

@dataclass
class StationCounters:
    """Model for station counters"""
    last_sample_timestamp: datetime
    mac:str
    tx_Mbps: Iterable[float]
    last_txBytes: int
    rx_Mbps: Iterable[float]
    last_rxBytes: int
    rx_pps: float
    last_rxPacketCount: int
    tx_pps: float
    last_txPacketCount: int
    uplinkMCS: int
    lastDataUplinkRate: int
    lastDataDownlinkRate: int
    SignalStrength: Iterable[int]
    uplinkShortGuard: int
    downlinkMCS: int
    avgSignalStrengthByChain: int
    signalNoiseRatio: int
    band: str
    inferences_results: Iterable[float]
