"""Tests for oinker HTTP layer."""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest

from oinker._config import OinkerConfig
from oinker._exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
)
from oinker._http import HttpClient


class TestHttpClient:
    """Tests for HttpClient."""

    async def test_context_manager(self, config_no_retry: OinkerConfig) -> None:
        """HttpClient should work as async context manager."""
        async with HttpClient(config_no_retry) as client:
            assert client._client is not None
        assert client._client is None

    async def test_post_includes_auth(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
    ) -> None:
        """POST requests should include authentication."""
        mock_httpx_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "data": "test"}
        )

        async with http_client_no_retry:
            await http_client_no_retry.post("/test")

        mock_httpx_client.post.assert_called_once()
        call_kwargs = mock_httpx_client.post.call_args[1]
        assert call_kwargs["json"]["apikey"] == "pk1_test_key"
        assert call_kwargs["json"]["secretapikey"] == "sk1_test_secret"

    async def test_post_without_auth(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
    ) -> None:
        """POST requests can skip authentication."""
        mock_httpx_client.post.return_value = httpx.Response(200, json={"status": "SUCCESS"})

        async with http_client_no_retry:
            await http_client_no_retry.post("/test", authenticated=False)

        call_kwargs = mock_httpx_client.post.call_args[1]
        assert "apikey" not in call_kwargs["json"]

    async def test_post_with_data(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
    ) -> None:
        """POST requests should include additional data."""
        mock_httpx_client.post.return_value = httpx.Response(200, json={"status": "SUCCESS"})

        async with http_client_no_retry:
            await http_client_no_retry.post("/test", data={"extra": "data"})

        call_kwargs = mock_httpx_client.post.call_args[1]
        assert call_kwargs["json"]["extra"] == "data"


class TestHttpClientErrorHandling:
    """Tests for HTTP error handling."""

    @pytest.mark.parametrize(
        ("status_code", "expected_exception"),
        [
            (401, AuthenticationError),
            (403, AuthorizationError),
            (404, NotFoundError),
            (429, RateLimitError),
        ],
    )
    async def test_http_error_codes(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
        status_code: int,
        expected_exception: type[Exception],
    ) -> None:
        """HTTP error codes should raise appropriate exceptions."""
        mock_httpx_client.post.return_value = httpx.Response(
            status_code, json={"status": "ERROR", "message": "Test error"}
        )

        async with http_client_no_retry:
            with pytest.raises(expected_exception):
                await http_client_no_retry.post("/test")

    @pytest.mark.parametrize(
        ("message", "expected_exception"),
        [
            ("Invalid API key provided", AuthenticationError),
            ("Authentication failed", AuthenticationError),
            ("Not authorized for this domain", AuthorizationError),
            ("Permission denied", AuthorizationError),
            ("Domain not found", NotFoundError),
            ("Record does not exist", NotFoundError),
        ],
    )
    async def test_api_error_messages(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
        message: str,
        expected_exception: type[Exception],
    ) -> None:
        """API error messages should map to appropriate exceptions."""
        mock_httpx_client.post.return_value = httpx.Response(
            200, json={"status": "ERROR", "message": message}
        )

        async with http_client_no_retry:
            with pytest.raises(expected_exception):
                await http_client_no_retry.post("/test")

    async def test_generic_api_error(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
    ) -> None:
        """Unknown API errors should raise APIError."""
        mock_httpx_client.post.return_value = httpx.Response(
            200, json={"status": "ERROR", "message": "Something unexpected"}
        )

        async with http_client_no_retry:
            with pytest.raises(APIError) as exc_info:
                await http_client_no_retry.post("/test")

        assert exc_info.value.message == "Something unexpected"

    async def test_rate_limit_retry_after(
        self,
        http_client_no_retry: HttpClient,
        mock_httpx_client: AsyncMock,
    ) -> None:
        """RateLimitError should include retry_after from headers."""
        response = httpx.Response(
            429,
            json={"status": "ERROR", "message": "Rate limited"},
            headers={"Retry-After": "30"},
        )
        mock_httpx_client.post.return_value = response

        async with http_client_no_retry:
            with pytest.raises(RateLimitError) as exc_info:
                await http_client_no_retry.post("/test")

        assert exc_info.value.retry_after == 30.0


class TestHttpClientRetry:
    """Tests for HTTP retry logic."""

    async def test_retry_on_connection_error(self) -> None:
        """Connection errors should trigger retries."""
        config = OinkerConfig(
            api_key="pk1_test",
            secret_key="sk1_test",
            max_retries=2,
            retry_delay=0.01,
        )
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.Response(200, json={"status": "SUCCESS"}),
        ]

        async with HttpClient(config, client=mock_client) as http:
            result = await http.post("/test")

        assert result["status"] == "SUCCESS"
        assert mock_client.post.call_count == 2

    async def test_retry_exhausted(self) -> None:
        """Exhausted retries should raise APIError."""
        config = OinkerConfig(
            api_key="pk1_test",
            secret_key="sk1_test",
            max_retries=1,
            retry_delay=0.01,
        )
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")

        async with HttpClient(config, client=mock_client) as http:
            with pytest.raises(APIError, match="failed after"):
                await http.post("/test")

        assert mock_client.post.call_count == 2  # Initial + 1 retry

    async def test_no_retry_on_rate_limit(self) -> None:
        """Rate limit errors should not be retried by HTTP layer."""
        config = OinkerConfig(
            api_key="pk1_test",
            secret_key="sk1_test",
            max_retries=2,
            retry_delay=0.01,
        )
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            429, json={"status": "ERROR", "message": "Rate limited"}
        )

        async with HttpClient(config, client=mock_client) as http:
            with pytest.raises(RateLimitError):
                await http.post("/test")

        # Should only be called once - no retries for rate limits
        assert mock_client.post.call_count == 1
