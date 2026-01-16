"""Domain operations for the Porkbun API.

Provides domain management including nameservers, URL forwarding, and glue records.
"""

from oinker.domains._api import AsyncDomainsAPI
from oinker.domains._sync import SyncDomainsAPI
from oinker.domains._types import (
    DomainAvailability,
    DomainInfo,
    DomainLabel,
    DomainPricing,
    GlueRecord,
    URLForward,
    URLForwardCreate,
    URLForwardType,
)

__all__ = [
    # API classes
    "AsyncDomainsAPI",
    "SyncDomainsAPI",
    # Domain types
    "DomainInfo",
    "DomainLabel",
    "DomainAvailability",
    "DomainPricing",
    # URL forwarding
    "URLForward",
    "URLForwardCreate",
    "URLForwardType",
    # Glue records
    "GlueRecord",
]
