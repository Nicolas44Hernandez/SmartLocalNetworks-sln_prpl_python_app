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
    status: bool
    probability: float

    def to_dict(self):
        """Convert the dataclass instance to a dictionary."""
        return {
            "station": self.station,
            "status": self.status,
            "probability": self.probability,
        }

@dataclass
class boxStatsSample:
    band: str
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
    errorsReceived: int # tx_ber / tx_err_pps
    errorsSent: int # tx_ber / tx_err_pps
    timestamp: datetime

    def to_dict(self):
        """Convert the dataclass instance to a dictionary."""
        return {
            "band": self.band,
            "bytesReceived": self.bytesReceived,
            "bytesSent": self.bytesSent,
            "noise": self.noise,
            "load": self.load,
            "freeTime": self.freeTime,
            "rxTime": self.rxTime,
            "vendorStats_glitch": self.vendorStats_glitch,
            "obssTime": self.obssTime,
            "txTime": self.txTime,
            "intTime": self.intTime,
            "noise_air": self.noise_air,
            "packetsReceived": self.packetsReceived,
            "packetsSent": self.packetsSent,
            "errorsReceived": self.errorsReceived,
            "errorsSent": self.errorsSent,
            "timestamp": self.timestamp.isoformat(timespec='milliseconds') + 'Z',
        }

@dataclass
class stationStatsSample:
    station: str
    band: str
    txBytes: int
    rxBytes: int
    uplinkMCS: int
    lastDataUplinkRate: int
    lastDataDownlinkRate: int
    signalStrength: int
    avgSignalStrengthByChain: int
    uplinkShortGuard: int
    downlinkMCS: int
    inactive: int
    signalNoiseRatio: int
    rxPacketCount: int # pps
    txPacketCount: int # pps
    txErrors: int
    timestamp: datetime

    def to_dict(self):
        """Convert the dataclass instance to a dictionary."""
        return {
            "station": self.station,
            "band": self.band,
            "txBytes": self.txBytes,
            "rxBytes": self.rxBytes,
            "uplinkMCS": self.uplinkMCS,
            "lastDataUplinkRate": self.lastDataUplinkRate,
            "lastDataDownlinkRate": self.lastDataDownlinkRate,
            "signalStrength": self.signalStrength,
            "avgSignalStrengthByChain": self.avgSignalStrengthByChain,
            "uplinkShortGuard": self.uplinkShortGuard,
            "downlinkMCS": self.downlinkMCS,
            "inactive": self.inactive,
            "signalNoiseRatio": self.signalNoiseRatio,
            "rxPacketCount": self.rxPacketCount,
            "txPacketCount": self.txPacketCount,
            "txErrors": self.txErrors,
            "timestamp": self.timestamp.isoformat(timespec='milliseconds') + 'Z',
        }

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
    tx_err_pps: float
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
    inactive: int
    avgSignalStrengthByChain: int
    signalNoiseRatio: int
    last_txErrors: int
    tx_err_pps: float
    tx_ber: float
    band: str
    inferences_results: Iterable[SingleStationInferenceResult]

    def inference_result_to_str(self) -> str:
        """used to print inference results"""
        return ' '.join(
            f"({'ON' if inference_result.status else 'OFF'} p:{inference_result.probability:.6f}) "
            for inference_result in self.inferences_results
        )


@dataclass
class BoxDataForInferenceInput:
    """Model for box data inference input"""
    obssTime: int
    rxTime: int
    txTime: int
    tx_Mbps: float
    rx_Mbps: float
    rx_pps: float
    tx_pps: float

    def to_dict(self):
        """Convert the dataclass instance to a dictionary."""
        return {
            "box_obssTime" : self.obssTime,
            "box_rxTime" : self.rxTime,
            "box_txTime" : self.txTime,
            "box_tx_Mbps" : self.tx_Mbps,
            "box_rx_Mbps" : self.rx_Mbps,
            "box_rx_pps" : self.rx_pps,
            "box_tx_pps" : self.tx_pps,
        }


@dataclass
class StationDataForInferenceInput:
    """Model for station data inference input"""
    station: str
    signalStrength: int
    downlinkMCS: float
    uplinkMCS: float
    uplinkShortGuard: float
    tx_Mbps: float
    rx_Mbps: float
    rx_pps: float
    tx_pps: float
    tx_err_pps: float

    def to_dict(self):
        """Convert the dataclass instance to a dictionary."""
        return {
            "station" : self.station,
            "signalStrength" : self.signalStrength,
            "downlinkMCS" : self.downlinkMCS,
            "uplinkMCS" : self.uplinkMCS,
            "uplinkShortGuard" : self.uplinkShortGuard,
            "tx_Mbps" : self.tx_Mbps,
            "rx_Mbps" : self.rx_Mbps,
            "rx_pps" : self.rx_pps,
            "tx_pps" : self.tx_pps,
            "tx_err_pps" : self.tx_err_pps,
        }


@dataclass
class InferencesInput:
    """Model for inference input data"""
    box_data: BoxDataForInferenceInput
    stations_data: Iterable[StationDataForInferenceInput]

    def to_dict(self):
        """Convert the dataclass instance to a dictionary."""
        return {
            "box_data" : self.box_data.to_dict(),
            "stations_data" : [station_data.to_dict() for station_data in self.stations_data]
        }
