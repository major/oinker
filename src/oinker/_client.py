"""AsyncPiglet - the async Porkbun API client.

This is the core async client. For sync usage, see Piglet in _sync.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from oinker._config import (
    BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    OinkerConfig,
)
from oinker._http import HttpClient
from oinker._types import PingResponse
from oinker.dns._api import AsyncDNSAPI

if TYPE_CHECKING:
    from types import TracebackType


class AsyncPiglet:
    """Async client for the Porkbun API.

    Use as an async context manager for proper resource cleanup:

        async with AsyncPiglet() as piglet:
            pong = await piglet.ping()
            print(f"Your IP: {pong.your_ip}")

    Credentials are loaded from environment variables by default:
        - PORKBUN_API_KEY
        - PORKBUN_SECRET_KEY

    Or pass them explicitly:

        async with AsyncPiglet(api_key="pk1_...", secret_key="sk1_...") as piglet:
            ...
    """

    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        _http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize the async Porkbun client.

        Args:
            api_key: Porkbun API key. Falls back to PORKBUN_API_KEY env var.
            secret_key: Porkbun secret key. Falls back to PORKBUN_SECRET_KEY env var.
            base_url: Override the default API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts for transient failures.
            _http_client: Pre-configured httpx client (for testing).
        """
        self._config = OinkerConfig(
            api_key=api_key or "",
            secret_key=secret_key or "",
            base_url=base_url or BASE_URL,
            timeout=timeout or DEFAULT_TIMEOUT,
            max_retries=max_retries if max_retries is not None else DEFAULT_MAX_RETRIES,
        )
        self._http = HttpClient(self._config, client=_http_client)
        self._dns = AsyncDNSAPI(self._http)

    @property
    def dns(self) -> AsyncDNSAPI:
        """Access DNS operations.

        Returns:
            AsyncDNSAPI instance for DNS management.
        """
        return self._dns

    async def __aenter__(self) -> AsyncPiglet:
        """Enter async context manager."""
        await self._http.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager."""
        await self._http.__aexit__(exc_type, exc_val, exc_tb)

    async def ping(self) -> PingResponse:
        """Test API connectivity and authentication.

        Returns:
            PingResponse with your public IP address.

        Raises:
            AuthenticationError: If credentials are invalid.
            APIError: If the request fails.
        """
        data = await self._http.post("/ping")
        return PingResponse(your_ip=data.get("yourIp", ""))
