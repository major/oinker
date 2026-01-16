"""DNSSEC management for oinker."""

from oinker.dnssec._api import AsyncDNSSECAPI
from oinker.dnssec._sync import SyncDNSSECAPI
from oinker.dnssec._types import DNSSECRecord, DNSSECRecordCreate

__all__ = [
    "AsyncDNSSECAPI",
    "SyncDNSSECAPI",
    "DNSSECRecord",
    "DNSSECRecordCreate",
]
