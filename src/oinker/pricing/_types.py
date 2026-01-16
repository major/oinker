"""Pricing type definitions for oinker.

Dataclasses for TLD pricing information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TLDPricing:
    """Pricing information for a top-level domain.

    Attributes:
        tld: The top-level domain (e.g., "com", "net", "org").
        registration: Registration price as a string (e.g., "9.68").
        renewal: Renewal price as a string.
        transfer: Transfer price as a string.
    """

    tld: str
    registration: str
    renewal: str
    transfer: str

    @classmethod
    def from_api_response(cls, tld: str, data: dict[str, Any]) -> TLDPricing:
        """Create from API response data.

        Args:
            tld: The top-level domain name.
            data: The pricing data dictionary for this TLD.

        Returns:
            A TLDPricing instance.
        """
        return cls(
            tld=tld,
            registration=data.get("registration", ""),
            renewal=data.get("renewal", ""),
            transfer=data.get("transfer", ""),
        )
