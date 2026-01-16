"""DNS operations for the Porkbun API.

Provides type-safe DNS record management.
"""

from oinker.dns._api import AsyncDNSAPI
from oinker.dns._records import (
    AAAARecord,
    ALIASRecord,
    ARecord,
    CAARecord,
    CNAMERecord,
    DNSRecord,
    DNSRecordResponse,
    DNSRecordType,
    HTTPSRecord,
    MXRecord,
    NSRecord,
    SRVRecord,
    SSHFPRecord,
    SVCBRecord,
    TLSARecord,
    TXTRecord,
)
from oinker.dns._sync import SyncDNSAPI

__all__ = [
    # API classes
    "AsyncDNSAPI",
    "SyncDNSAPI",
    # Record types
    "ARecord",
    "AAAARecord",
    "MXRecord",
    "TXTRecord",
    "CNAMERecord",
    "ALIASRecord",
    "NSRecord",
    "SRVRecord",
    "TLSARecord",
    "CAARecord",
    "HTTPSRecord",
    "SVCBRecord",
    "SSHFPRecord",
    # Type aliases
    "DNSRecord",
    "DNSRecordType",
    "DNSRecordResponse",
]
