"""Piglet - synchronous wrapper around AsyncPiglet.

For scripts, CLI tools, and simple use cases where async isn't needed.
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from types import TracebackType
from typing import TYPE_CHECKING, Any, TypeVar

from oinker._client import AsyncPiglet
from oinker._types import PingResponse

if TYPE_CHECKING:
    import httpx

T = TypeVar("T")


class Piglet:
    """Synchronous client for the Porkbun API.

    A convenience wrapper around AsyncPiglet for non-async code.

        piglet = Piglet()
        pong = piglet.ping()
        print(f"Your IP: {pong.your_ip}")
        piglet.close()

    Or use as a context manager:

        with Piglet() as piglet:
            pong = piglet.ping()

    Credentials are loaded from environment variables by default:
        - PORKBUN_API_KEY
        - PORKBUN_SECRET_KEY
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
        """Initialize the sync Porkbun client.

        Args:
            api_key: Porkbun API key. Falls back to PORKBUN_API_KEY env var.
            secret_key: Porkbun secret key. Falls back to PORKBUN_SECRET_KEY env var.
            base_url: Override the default API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts for transient failures.
            _http_client: Pre-configured httpx client (for testing).
        """
        self._async_client = AsyncPiglet(
            api_key=api_key,
            secret_key=secret_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            _http_client=_http_client,
        )
        self._loop: asyncio.AbstractEventLoop | None = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create an event loop for running async code."""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop

    def _run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run an async coroutine synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(coro)

    def __enter__(self) -> Piglet:
        """Enter sync context manager."""
        self._run(self._async_client.__aenter__())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit sync context manager."""
        self._run(self._async_client.__aexit__(exc_type, exc_val, exc_tb))

    def close(self) -> None:
        """Close the client and release resources."""
        self._run(self._async_client.__aexit__(None, None, None))
        if self._loop is not None and not self._loop.is_running():
            self._loop.close()
            self._loop = None

    def ping(self) -> PingResponse:
        """Test API connectivity and authentication.

        Returns:
            PingResponse with your public IP address.

        Raises:
            AuthenticationError: If credentials are invalid.
            APIError: If the request fails.
        """
        return self._run(self._async_client.ping())
