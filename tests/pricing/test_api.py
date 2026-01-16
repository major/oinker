"""Tests for the pricing API."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from oinker._exceptions import APIError
from oinker.pricing import TLDPricing, get_pricing


class TestGetPricing:
    """Tests for get_pricing function."""

    async def test_returns_tld_pricing_dict(self) -> None:
        """get_pricing() returns dict mapping TLD to TLDPricing."""
        mock_response = httpx.Response(
            200,
            json={
                "status": "SUCCESS",
                "pricing": {
                    "com": {"registration": "9.68", "renewal": "9.68", "transfer": "9.68"},
                    "net": {"registration": "12.00", "renewal": "12.00", "transfer": "12.00"},
                },
            },
        )

        with patch("oinker.pricing._api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            result = await get_pricing()

        assert len(result) == 2
        assert "com" in result
        assert "net" in result
        assert isinstance(result["com"], TLDPricing)
        assert result["com"].registration == "9.68"
        assert result["net"].renewal == "12.00"

    async def test_raises_api_error_on_failure_status(self) -> None:
        """get_pricing() raises APIError when status is ERROR."""
        mock_response = httpx.Response(
            200,
            json={"status": "ERROR", "message": "Something went wrong"},
        )

        with patch("oinker.pricing._api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            with pytest.raises(APIError, match="Something went wrong"):
                await get_pricing()

    async def test_raises_api_error_on_connection_failure(self) -> None:
        """get_pricing() raises APIError on connection failure."""
        with patch("oinker.pricing._api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.ConnectError("Connection failed")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            with pytest.raises(APIError, match="Failed to connect"):
                await get_pricing()

    async def test_raises_api_error_on_invalid_json(self) -> None:
        """get_pricing() raises APIError on invalid JSON response."""
        mock_response = httpx.Response(200, content=b"not json")

        with patch("oinker.pricing._api.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            with pytest.raises(APIError, match="Invalid JSON"):
                await get_pricing()


class TestTLDPricing:
    """Tests for TLDPricing dataclass."""

    def test_from_api_response(self) -> None:
        """TLDPricing.from_api_response() creates instance from API data."""
        data = {"registration": "9.68", "renewal": "10.00", "transfer": "9.68"}
        pricing = TLDPricing.from_api_response("com", data)

        assert pricing.tld == "com"
        assert pricing.registration == "9.68"
        assert pricing.renewal == "10.00"
        assert pricing.transfer == "9.68"

    def test_from_api_response_handles_missing_fields(self) -> None:
        """TLDPricing.from_api_response() handles missing fields gracefully."""
        data: dict[str, str] = {}
        pricing = TLDPricing.from_api_response("org", data)

        assert pricing.tld == "org"
        assert pricing.registration == ""
        assert pricing.renewal == ""
        assert pricing.transfer == ""
