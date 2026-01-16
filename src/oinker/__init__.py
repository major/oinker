"""Oinker - A delightfully Pythonic library for managing DNS at Porkbun.

from oinker import Piglet, AsyncPiglet

# Async (recommended for performance)
async with AsyncPiglet() as piglet:
    pong = await piglet.ping()
    print(f"Your IP: {pong.your_ip}")

# Sync (for scripts and simple use)
with Piglet() as piglet:
    pong = piglet.ping()
"""

from oinker._client import AsyncPiglet
from oinker._exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    OinkerError,
    RateLimitError,
    ValidationError,
)
from oinker._sync import Piglet
from oinker._types import PingResponse
from oinker.dns import (
    AAAARecord,
    ALIASRecord,
    ARecord,
    CAARecord,
    CNAMERecord,
    DNSRecord,
    DNSRecordResponse,
    HTTPSRecord,
    MXRecord,
    NSRecord,
    SRVRecord,
    SSHFPRecord,
    SVCBRecord,
    TLSARecord,
    TXTRecord,
)
from oinker.dnssec import DNSSECRecord, DNSSECRecordCreate
from oinker.domains import (
    DomainAvailability,
    DomainInfo,
    DomainLabel,
    DomainPricing,
    GlueRecord,
    URLForward,
    URLForwardCreate,
)
from oinker.pricing import TLDPricing, get_pricing, get_pricing_sync
from oinker.ssl import SSLBundle

__all__ = [
    # Clients
    "AsyncPiglet",
    "Piglet",
    # Types
    "PingResponse",
    # DNS Records
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
    "DNSRecord",
    "DNSRecordResponse",
    # Domain Types
    "DomainInfo",
    "DomainLabel",
    "DomainAvailability",
    "DomainPricing",
    "URLForward",
    "URLForwardCreate",
    "GlueRecord",
    # DNSSEC Types
    "DNSSECRecord",
    "DNSSECRecordCreate",
    # SSL Types
    "SSLBundle",
    # Pricing
    "TLDPricing",
    "get_pricing",
    "get_pricing_sync",
    # Exceptions
    "OinkerError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "APIError",
]

__version__ = "0.1.0"
