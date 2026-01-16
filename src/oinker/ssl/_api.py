"""Async SSL API operations for the Porkbun API.

Provides SSL certificate retrieval operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from oinker.ssl._types import SSLBundle

if TYPE_CHECKING:
    from oinker._http import HttpClient


class AsyncSSLAPI:
    """Async SSL operations for the Porkbun API.

    Accessed via `piglet.ssl.*` methods.
    """

    def __init__(self, http: HttpClient) -> None:
        """Initialize SSL API.

        Args:
            http: The HTTP client for making requests.
        """
        self._http = http

    async def retrieve(self, domain: str) -> SSLBundle:
        """Retrieve the SSL certificate bundle for a domain.

        Args:
            domain: The domain name (e.g., "example.com").

        Returns:
            SSLBundle containing certificate chain, private key, and public key.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found or has no SSL certificate.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/ssl/retrieve/{domain}")
        return SSLBundle.from_api_response(data)
