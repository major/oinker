"""HTTP layer with retry logic for oinker.

Wraps httpx.AsyncClient with automatic retry for transient failures
and proper error handling for Porkbun API responses.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import httpx

import oinker
from oinker._config import OinkerConfig
from oinker._exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger(__name__)

_HTTP_STATUS_TO_EXCEPTION = {
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
}

_ERROR_MESSAGE_PATTERNS = [
    (["invalid api key", "authentication"], AuthenticationError),
    (["not authorized", "permission"], AuthorizationError),
    (["not found", "does not exist"], NotFoundError),
]


class HttpClient:
    """Async HTTP client with retry logic for the Porkbun API.

    Handles authentication, retries, and error translation.
    """

    def __init__(
        self,
        config: OinkerConfig,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            config: Oinker configuration with credentials and settings.
            client: Optional pre-configured httpx client for testing.
        """
        self._config = config
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> HttpClient:
        """Enter async context manager."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
                timeout=self._config.timeout,
                headers={"User-Agent": f"oinker/{oinker.__version__}"},
            )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit async context manager, closing client if we own it."""
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def post(
        self,
        endpoint: str,
        data: Mapping[str, Any] | None = None,
        *,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        """Make an authenticated POST request to the Porkbun API.

        Args:
            endpoint: API endpoint path (e.g., "/ping").
            data: Optional additional request data.
            authenticated: Whether to include auth credentials.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            AuthenticationError: Invalid credentials.
            AuthorizationError: Not authorized for this resource.
            NotFoundError: Domain or record not found.
            RateLimitError: Rate limit exceeded.
            APIError: Other API errors.
        """
        if self._client is None:
            msg = "HTTP client not initialized. Use 'async with' context manager."
            raise RuntimeError(msg)

        # Build request body
        body: dict[str, Any] = {}
        if authenticated:
            body.update(self._config.auth_body)
        if data:
            body.update(data)

        last_error: Exception | None = None
        delay = self._config.retry_delay

        for attempt in range(self._config.max_retries + 1):
            try:
                logger.debug("POST %s", endpoint)
                response = await self._client.post(endpoint, json=body)
                logger.debug("Response %s: %s", response.status_code, response.text[:200])
                return self._handle_response(response)

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self._config.max_retries:
                    logger.warning(
                        "Request failed (attempt %d/%d): %s. Retrying in %.1fs...",
                        attempt + 1,
                        self._config.max_retries + 1,
                        e,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                continue

            except RateLimitError:
                # Don't retry rate limits automatically here - let caller decide
                raise

        # All retries exhausted
        msg = f"Request failed after {self._config.max_retries + 1} attempts"
        raise APIError(msg) from last_error

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate errors.

        Args:
            response: The httpx response object.

        Returns:
            Parsed JSON response.

        Raises:
            Various OinkerError subclasses based on response.
        """
        try:
            data = response.json()
        except ValueError as e:
            msg = f"Invalid JSON response: {response.text[:200]}"
            raise APIError(msg, status_code=response.status_code) from e

        message = data.get("message", "Unknown error")

        self._raise_for_http_status(response, message)

        if data.get("status", "").upper() == "ERROR":
            self._raise_for_api_error(message, response.status_code)

        return data

    def _raise_for_http_status(self, response: httpx.Response, message: str) -> None:
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                retry_after=float(retry_after) if retry_after else None,
            )

        exc_class = _HTTP_STATUS_TO_EXCEPTION.get(response.status_code)
        if exc_class:
            raise exc_class(message)

    def _raise_for_api_error(self, message: str, status_code: int) -> None:
        msg_lower = message.lower()
        for patterns, exc_class in _ERROR_MESSAGE_PATTERNS:
            if any(pattern in msg_lower for pattern in patterns):
                raise exc_class(message)
        raise APIError(message, status_code=status_code)
