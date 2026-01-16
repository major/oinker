"""Pricing module for domain TLD pricing information.

This module provides access to Porkbun's domain pricing API,
which does not require authentication.

Example:
    >>> from oinker.pricing import get_pricing, get_pricing_sync
    >>> pricing = await get_pricing()
    >>> print(pricing["com"].registration)
    "9.68"
"""

from oinker.pricing._api import get_pricing, get_pricing_sync
from oinker.pricing._types import TLDPricing

__all__ = [
    "get_pricing",
    "get_pricing_sync",
    "TLDPricing",
]
