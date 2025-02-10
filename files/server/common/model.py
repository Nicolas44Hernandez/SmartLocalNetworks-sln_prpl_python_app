"""Data model for 5GHz band on/off manager package"""

import queue
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


samples_queue = queue.Queue()


@dataclass
class SingleStationInferenceResult:
    """Model for single station inference result"""
    station: str
    prediction: bool
    probability: float

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
    signalStrength: Iterable[int]
    uplinkShortGuard: int
    downlinkMCS: int
    avgSignalStrengthByChain: int
    signalNoiseRatio: int
    band: str
    inferences_results: Iterable[SingleStationInferenceResult]

    def inference_result_to_str(self) -> str:
        """used to print inference results"""
        return ' '.join(
            f"({'ON' if inference_result.prediction else 'OFF'} p:{inference_result.probability:.2f}) "
            for inference_result in self.inferences_results
        )


@dataclass
class BoxDataForInferenceInput:
    """Model for box data inference input"""
    rx_Mbps: float
    rx_Mbps_lag1: float
    rx_Mbps_lag2: float
    rx_Mbps_lag3: float
    rx_Mbps_avg3: float
    rx_Mbps_avg5: float
    rx_Mbps_avg7:float
    tx_Mbps: float
    tx_Mbps_lag1: float
    tx_Mbps_lag2: float
    tx_Mbps_lag3: float
    tx_Mbps_avg3: float
    tx_Mbps_avg5: float
    tx_Mbps_avg7: float
    noise: int
    noise_lag3: int
    noise_avg3: float
    noise_avg5: float
    noise_avg7: float
    rx_pps: float
    tx_pps: float
    load: int
    freeTime: int
    rxTime: int
    vendorStats_glitch: int
    obssTime: int
    txTime: int
    intTime: int
    noise_air: int
    tx_err_ps: float
    tx_ber: float


@dataclass
class StationDataForInferenceInput:
    """Model for station data inference input"""
    station: str
    rx_Mbps: float
    rx_Mbps_lag1: float
    rx_Mbps_lag2: float
    rx_Mbps_lag3: float
    rx_Mbps_lag5: float
    rx_Mbps_lag7: float
    rx_Mbps_avg3: float
    rx_Mbps_avg5: float
    rx_Mbps_avg7: float
    rx_Mbps_avg10: float
    tx_Mbps: float
    tx_Mbps_lag1: float
    tx_Mbps_avg3: float
    tx_Mbps_avg5: float
    signalStrength: int
    signalStrength_lag1: int
    signalStrength_lag2: int
    signalStrength_lag3: int
    signalStrength_lag5: int
    signalStrength_lag7: int
    signalStrength_avg3: float
    signalStrength_avg5: float
    signalStrength_avg7: float
    signalStrength_avg10: float
    rx_pps: float
    tx_pps: float
    uplinkMCS: float
    lastDataUplinkRate: float
    lastDataDownlinkRate: float
    uplinkShortGuard: float
    downlinkMCS: float
    avgSignalStrengthByChain: float
    signalNoiseRatio: float

