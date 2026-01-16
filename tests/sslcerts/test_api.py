"""Tests for async SSL API operations."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from conftest import make_response

from oinker import AsyncPiglet, Piglet
from oinker._config import OinkerConfig
from oinker._exceptions import AuthenticationError, NotFoundError


class TestAsyncSSLAPIRetrieve:
    """Tests for ssl.retrieve() operation."""

    async def test_retrieve_ssl_bundle(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        cert = "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"
        key = "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----"
        pub = "-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----"
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "certificatechain": cert,
                "privatekey": key,
                "publickey": pub,
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            bundle = await piglet.ssl.retrieve("example.com")

        assert bundle.certificate_chain == cert
        assert bundle.private_key == key
        assert bundle.public_key == pub

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/ssl/retrieve/example.com"

    async def test_retrieve_empty_bundle(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "certificatechain": "",
                "privatekey": "",
                "publickey": "",
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            bundle = await piglet.ssl.retrieve("example.com")

        assert bundle.certificate_chain == ""
        assert bundle.private_key == ""
        assert bundle.public_key == ""


class TestSyncSSLAPI:
    """Tests for sync SSL API wrapper."""

    def test_sync_retrieve_ssl(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        cert = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "certificatechain": cert,
                "privatekey": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
                "publickey": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
            }
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            bundle = piglet.ssl.retrieve("example.com")

        assert bundle.certificate_chain == cert
        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/ssl/retrieve/example.com"


class TestSSLAPIErrors:
    """Tests for SSL API error handling."""

    @pytest.mark.parametrize(
        ("status_code", "message", "expected_exception"),
        [
            (401, "Invalid API key", AuthenticationError),
            (404, "Domain not found", NotFoundError),
        ],
    )
    async def test_retrieve_error_handling(
        self,
        mock_httpx_client: AsyncMock,
        config: OinkerConfig,
        status_code: int,
        message: str,
        expected_exception: type[Exception],
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {"status": "ERROR", "message": message}, status_code
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            with pytest.raises(expected_exception):
                await piglet.ssl.retrieve("example.com")
