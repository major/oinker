"""Tests for async DNSSEC API operations."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from oinker import AsyncPiglet, Piglet
from oinker._config import OinkerConfig
from oinker._exceptions import AuthenticationError, NotFoundError
from oinker.dnssec import DNSSECRecordCreate


def make_response(data: dict[str, Any], status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=data)


class TestAsyncDNSSECAPIList:
    """Tests for dnssec.list() operation."""

    async def test_list_dnssec_records(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": {
                    "64087": {
                        "keyTag": "64087",
                        "alg": "13",
                        "digestType": "2",
                        "digest": "15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D553",
                    },
                    "64086": {
                        "keyTag": "64086",
                        "alg": "13",
                        "digestType": "2",
                        "digest": "85E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D553",
                    },
                },
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            records = await piglet.dnssec.list("example.com")

        assert len(records) == 2
        key_tags = {r.key_tag for r in records}
        assert "64087" in key_tags
        assert "64086" in key_tags

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/dns/getDnssecRecords/example.com"

    async def test_list_empty_records(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "records": {}})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            records = await piglet.dnssec.list("example.com")

        assert records == []


class TestAsyncDNSSECAPICreate:
    """Tests for dnssec.create() operation."""

    async def test_create_dnssec_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        record = DNSSECRecordCreate(
            key_tag="64087",
            algorithm="13",
            digest_type="2",
            digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dnssec.create("example.com", record)

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/dns/createDnssecRecord/example.com"
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("keyTag") == "64087"
        assert request_json.get("alg") == "13"
        assert request_json.get("digestType") == "2"
        assert (
            request_json.get("digest")
            == "15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC"
        )

    async def test_create_dnssec_record_with_key_data(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        record = DNSSECRecordCreate(
            key_tag="64087",
            algorithm="13",
            digest_type="2",
            digest="15E445BD",
            max_sig_life="86400",
            key_data_flags="257",
            key_data_protocol="3",
            key_data_algorithm="13",
            key_data_public_key="ABCDEF123456",
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dnssec.create("example.com", record)

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("maxSigLife") == "86400"
        assert request_json.get("keyDataFlags") == "257"
        assert request_json.get("keyDataProtocol") == "3"
        assert request_json.get("keyDataAlgo") == "13"
        assert request_json.get("keyDataPubKey") == "ABCDEF123456"


class TestAsyncDNSSECAPIDelete:
    """Tests for dnssec.delete() operation."""

    async def test_delete_dnssec_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dnssec.delete("example.com", "64087")

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/dns/deleteDnssecRecord/example.com/64087"


class TestSyncDNSSECAPI:
    """Tests for sync DNSSEC API wrapper."""

    def test_sync_list_dnssec(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": {
                    "64087": {
                        "keyTag": "64087",
                        "alg": "13",
                        "digestType": "2",
                        "digest": "15E445BD",
                    }
                },
            }
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            records = piglet.dnssec.list("example.com")

        assert len(records) == 1
        assert records[0].key_tag == "64087"

    def test_sync_create_dnssec(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        record = DNSSECRecordCreate(
            key_tag="64087",
            algorithm="13",
            digest_type="2",
            digest="15E445BD",
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.dnssec.create("example.com", record)

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/dns/createDnssecRecord/example.com"

    def test_sync_delete_dnssec(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.dnssec.delete("example.com", "64087")

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/dns/deleteDnssecRecord/example.com/64087"


class TestDNSSECAPIErrors:
    """Tests for DNSSEC API error handling."""

    @pytest.mark.parametrize(
        ("status_code", "message", "expected_exception"),
        [
            (401, "Invalid API key", AuthenticationError),
            (404, "Domain not found", NotFoundError),
        ],
    )
    async def test_list_error_handling(
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
                await piglet.dnssec.list("example.com")

    @pytest.mark.parametrize(
        ("status_code", "message", "expected_exception"),
        [
            (401, "Invalid API key", AuthenticationError),
            (404, "Domain not found", NotFoundError),
        ],
    )
    async def test_create_error_handling(
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

        record = DNSSECRecordCreate(
            key_tag="64087",
            algorithm="13",
            digest_type="2",
            digest="15E445BD",
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            with pytest.raises(expected_exception):
                await piglet.dnssec.create("example.com", record)

    @pytest.mark.parametrize(
        ("status_code", "message", "expected_exception"),
        [
            (401, "Invalid API key", AuthenticationError),
            (404, "Record not found", NotFoundError),
        ],
    )
    async def test_delete_error_handling(
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
                await piglet.dnssec.delete("example.com", "64087")
