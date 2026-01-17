"""Pricing API operations for the Porkbun API.

Provides domain pricing information. This endpoint does not require authentication.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from oinker._exceptions import APIError
from oinker.pricing._types import TLDPricing

# Default pricing API URL
PRICING_URL = "https://api.porkbun.com/api/json/v3/pricing/get"

# Default timeout for pricing requests
DEFAULT_TIMEOUT = 30.0


async def get_pricing(
    request_timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, TLDPricing]:
    """Get default domain pricing for all supported TLDs.

    This endpoint does not require authentication.

    Args:
        request_timeout: Request timeout in seconds (default 30).

    Returns:
        Dictionary mapping TLD names to their pricing information.

    Raises:
        APIError: If the request fails.

    Example:
        >>> pricing = await get_pricing()
        >>> print(pricing["com"].registration)
        "9.68"
    """
    async with httpx.AsyncClient(timeout=request_timeout) as client:
        try:
            response = await client.post(PRICING_URL)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            msg = f"Failed to connect to pricing API: {e}"
            raise APIError(msg) from e

        try:
            data: dict[str, Any] = response.json()
        except ValueError as e:
            msg = f"Invalid JSON response: {response.text[:200]}"
            raise APIError(msg, status_code=response.status_code) from e

        status = data.get("status", "")
        if status.upper() != "SUCCESS":
            message = data.get("message", "Unknown error")
            raise APIError(message, status_code=response.status_code)

        pricing_data = data.get("pricing", {})
        return {
            tld: TLDPricing.from_api_response(tld, tld_data)
            for tld, tld_data in pricing_data.items()
        }


def get_pricing_sync(request_timeout: float = DEFAULT_TIMEOUT) -> dict[str, TLDPricing]:
    """Get default domain pricing for all supported TLDs (synchronous version).

    This endpoint does not require authentication.

    Args:
        request_timeout: Request timeout in seconds (default 30).

    Returns:
        Dictionary mapping TLD names to their pricing information.

    Raises:
        APIError: If the request fails.

    Example:
        >>> pricing = get_pricing_sync()
        >>> print(pricing["com"].registration)
        "9.68"
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_pricing(request_timeout))
    finally:
        loop.close()
