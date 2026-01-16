"""Tests for oinker client classes."""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx

from oinker import AsyncPiglet, Piglet, PingResponse


class TestAsyncPiglet:
    """Tests for AsyncPiglet."""

    async def test_context_manager(self) -> None:
        """AsyncPiglet should work as async context manager."""
        async with AsyncPiglet(api_key="test", secret_key="test") as piglet:
            assert piglet is not None

    async def test_ping(self) -> None:
        """ping() should return PingResponse with IP."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "yourIp": "203.0.113.42"}
        )

        async with AsyncPiglet(
            api_key="test", secret_key="test", _http_client=mock_client
        ) as piglet:
            result = await piglet.ping()

        assert isinstance(result, PingResponse)
        assert result.your_ip == "203.0.113.42"

    async def test_ping_called_correct_endpoint(self) -> None:
        """ping() should call /ping endpoint."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "yourIp": "1.2.3.4"}
        )

        async with AsyncPiglet(
            api_key="test", secret_key="test", _http_client=mock_client
        ) as piglet:
            await piglet.ping()

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args[0]
        assert call_args[0] == "/ping"


class TestPiglet:
    """Tests for sync Piglet wrapper."""

    def test_context_manager(self) -> None:
        """Piglet should work as sync context manager."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "yourIp": "1.2.3.4"}
        )

        with Piglet(api_key="test", secret_key="test", _http_client=mock_client) as piglet:
            assert piglet is not None

    def test_ping(self) -> None:
        """ping() should return PingResponse with IP."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "yourIp": "10.0.0.1"}
        )

        with Piglet(api_key="test", secret_key="test", _http_client=mock_client) as piglet:
            result = piglet.ping()

        assert isinstance(result, PingResponse)
        assert result.your_ip == "10.0.0.1"

    def test_close(self) -> None:
        """close() should release resources."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "yourIp": "1.2.3.4"}
        )

        piglet = Piglet(api_key="test", secret_key="test", _http_client=mock_client)
        piglet.close()
        # Should not raise
