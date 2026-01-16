"""Tests for async DNS API operations."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from oinker import ARecord, AsyncPiglet, MXRecord, Piglet, TXTRecord
from oinker._config import OinkerConfig
from oinker._exceptions import AuthenticationError, NotFoundError


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx.AsyncClient for testing."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def config() -> OinkerConfig:
    """Test configuration with credentials."""
    return OinkerConfig(api_key="pk1_test", secret_key="sk1_test")


def make_response(data: dict[str, Any], status_code: int = 200) -> httpx.Response:
    """Create a mock httpx.Response."""
    return httpx.Response(status_code, json=data)


class TestAsyncDNSAPIList:
    """Tests for dns.list() operation."""

    async def test_list_records_success(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": [
                    {
                        "id": "123",
                        "name": "example.com",
                        "type": "A",
                        "content": "1.2.3.4",
                        "ttl": "600",
                        "prio": "0",
                        "notes": "",
                    },
                    {
                        "id": "456",
                        "name": "www.example.com",
                        "type": "A",
                        "content": "1.2.3.4",
                        "ttl": "600",
                        "prio": "0",
                        "notes": "",
                    },
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            records = await piglet.dns.list("example.com")

        assert len(records) == 2
        assert records[0].id == "123"
        assert records[0].content == "1.2.3.4"
        assert records[1].name == "www.example.com"

    async def test_list_empty_records(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "records": []})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            records = await piglet.dns.list("example.com")

        assert records == []


class TestAsyncDNSAPIGet:
    """Tests for dns.get() operation."""

    async def test_get_record_by_id(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": [
                    {
                        "id": "123",
                        "name": "example.com",
                        "type": "A",
                        "content": "1.2.3.4",
                        "ttl": "600",
                        "prio": "0",
                        "notes": "",
                    }
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            record = await piglet.dns.get("example.com", "123")

        assert record is not None
        assert record.id == "123"
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert "/dns/retrieve/example.com/123" in str(call_args)

    async def test_get_record_not_found(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "records": []})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            record = await piglet.dns.get("example.com", "nonexistent")

        assert record is None


class TestAsyncDNSAPIGetByNameType:
    """Tests for dns.get_by_name_type() operation."""

    async def test_get_by_name_type_with_subdomain(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": [
                    {
                        "id": "456",
                        "name": "www.example.com",
                        "type": "A",
                        "content": "1.2.3.4",
                        "ttl": "600",
                        "prio": "0",
                        "notes": "",
                    }
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            records = await piglet.dns.get_by_name_type("example.com", "A", "www")

        assert len(records) == 1
        assert records[0].name == "www.example.com"
        call_args = mock_httpx_client.post.call_args
        assert "/dns/retrieveByNameType/example.com/A/www" in str(call_args)

    async def test_get_by_name_type_root_domain(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "records": []})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.get_by_name_type("example.com", "A")

        call_args = mock_httpx_client.post.call_args
        # Should NOT have a trailing subdomain
        assert "/dns/retrieveByNameType/example.com/A" in str(call_args)
        assert "/dns/retrieveByNameType/example.com/A/" not in str(call_args)


class TestAsyncDNSAPICreate:
    """Tests for dns.create() operation."""

    async def test_create_a_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "id": "789"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            record_id = await piglet.dns.create(
                "example.com", ARecord(content="1.2.3.4", name="www", ttl=600)
            )

        assert record_id == "789"
        call_args = mock_httpx_client.post.call_args
        assert "/dns/create/example.com" in str(call_args)

    async def test_create_mx_record_with_priority(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "id": "999"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            record_id = await piglet.dns.create(
                "example.com", MXRecord(content="mail.example.com", priority=10)
            )

        assert record_id == "999"
        call_args = mock_httpx_client.post.call_args
        # Verify the request body includes priority
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("prio") == "10"
        assert request_json.get("type") == "MX"


class TestAsyncDNSAPIEdit:
    """Tests for dns.edit() operation."""

    async def test_edit_record_by_id(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.edit("example.com", "123", ARecord(content="5.6.7.8", name="www"))

        call_args = mock_httpx_client.post.call_args
        assert "/dns/edit/example.com/123" in str(call_args)


class TestAsyncDNSAPIEditByNameType:
    """Tests for dns.edit_by_name_type() operation."""

    async def test_edit_by_name_type(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.edit_by_name_type(
                "example.com", "A", "www", content="5.6.7.8", ttl=1200
            )

        call_args = mock_httpx_client.post.call_args
        assert "/dns/editByNameType/example.com/A/www" in str(call_args)
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("content") == "5.6.7.8"
        assert request_json.get("ttl") == "1200"

    @pytest.mark.parametrize(
        ("kwargs", "expected_keys"),
        [
            ({"content": "1.2.3.4"}, {"content"}),
            ({"content": "1.2.3.4", "ttl": 1200}, {"content", "ttl"}),
            ({"content": "1.2.3.4", "priority": 5}, {"content", "prio"}),
            ({"content": "1.2.3.4", "notes": "test note"}, {"content", "notes"}),
            (
                {"content": "1.2.3.4", "ttl": 1200, "priority": 5, "notes": "all params"},
                {"content", "ttl", "prio", "notes"},
            ),
        ],
    )
    async def test_edit_by_name_type_optional_params(
        self,
        mock_httpx_client: AsyncMock,
        config: OinkerConfig,
        kwargs: dict[str, Any],
        expected_keys: set[str],
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.edit_by_name_type("example.com", "A", None, **kwargs)

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        auth_keys = {"secretapikey", "apikey"}
        actual_keys = set(request_json.keys()) - auth_keys
        assert actual_keys == expected_keys


class TestAsyncDNSAPIDelete:
    """Tests for dns.delete() operation."""

    async def test_delete_by_id(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.delete("example.com", "123")

        call_args = mock_httpx_client.post.call_args
        assert "/dns/delete/example.com/123" in str(call_args)


class TestAsyncDNSAPIDeleteByNameType:
    """Tests for dns.delete_by_name_type() operation."""

    async def test_delete_by_name_type_with_subdomain(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.delete_by_name_type("example.com", "A", "www")

        call_args = mock_httpx_client.post.call_args
        assert "/dns/deleteByNameType/example.com/A/www" in str(call_args)

    async def test_delete_by_name_type_root(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.delete_by_name_type("example.com", "TXT")

        call_args = mock_httpx_client.post.call_args
        assert "/dns/deleteByNameType/example.com/TXT" in str(call_args)


class TestRecordToAPIBody:
    """Tests for record serialization to API body."""

    async def test_a_record_serialization(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "id": "1"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.create(
                "example.com",
                ARecord(content="1.2.3.4", name="www", ttl=1200, notes="Test note"),
            )

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json["type"] == "A"
        assert request_json["content"] == "1.2.3.4"
        assert request_json["name"] == "www"
        assert request_json["ttl"] == "1200"
        assert request_json["notes"] == "Test note"

    async def test_txt_record_no_name(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "id": "1"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.dns.create("example.com", TXTRecord(content="v=spf1"))

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json["type"] == "TXT"
        assert "name" not in request_json


class TestSyncDNSAPI:
    """Tests for sync DNS API wrapper."""

    def test_sync_list_records(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": [
                    {
                        "id": "123",
                        "name": "example.com",
                        "type": "A",
                        "content": "1.2.3.4",
                        "ttl": "600",
                        "prio": "0",
                        "notes": "",
                    }
                ],
            }
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            records = piglet.dns.list("example.com")

        assert len(records) == 1
        assert records[0].id == "123"

    def test_sync_get_record(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "records": [
                    {
                        "id": "456",
                        "name": "www.example.com",
                        "type": "A",
                        "content": "1.2.3.4",
                        "ttl": "600",
                        "prio": "0",
                        "notes": "",
                    }
                ],
            }
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            record = piglet.dns.get("example.com", "456")

        assert record is not None
        assert record.id == "456"

    def test_sync_create_record(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "id": "789"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            record_id = piglet.dns.create("example.com", ARecord(content="1.2.3.4", name="www"))

        assert record_id == "789"

    def test_sync_edit_record(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.dns.edit("example.com", "123", ARecord(content="5.6.7.8", name="www"))

        call_args = mock_httpx_client.post.call_args
        assert "/dns/edit/example.com/123" in str(call_args)

    def test_sync_delete_record(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.dns.delete("example.com", "123")

        call_args = mock_httpx_client.post.call_args
        assert "/dns/delete/example.com/123" in str(call_args)

    def test_sync_get_by_name_type(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "records": []})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            records = piglet.dns.get_by_name_type("example.com", "A", "www")

        assert records == []
        call_args = mock_httpx_client.post.call_args
        assert "/dns/retrieveByNameType/example.com/A/www" in str(call_args)

    def test_sync_edit_by_name_type(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.dns.edit_by_name_type("example.com", "A", "www", content="5.6.7.8")

        call_args = mock_httpx_client.post.call_args
        assert "/dns/editByNameType/example.com/A/www" in str(call_args)

    def test_sync_delete_by_name_type(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.dns.delete_by_name_type("example.com", "A", "www")

        call_args = mock_httpx_client.post.call_args
        assert "/dns/deleteByNameType/example.com/A/www" in str(call_args)


class TestDNSErrorHandling:
    """Tests for DNS error propagation from HTTP layer."""

    async def test_authentication_error_propagates(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {"status": "ERROR", "message": "Invalid API Key"}, status_code=200
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            with pytest.raises(AuthenticationError, match="Invalid API Key"):
                await piglet.dns.list("example.com")

    async def test_not_found_error_on_delete(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {"status": "ERROR", "message": "Record not found"}, status_code=200
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            with pytest.raises(NotFoundError, match="Record not found"):
                await piglet.dns.delete("example.com", "nonexistent")

    async def test_not_found_error_on_edit(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {"status": "ERROR", "message": "Record does not exist"}, status_code=200
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            with pytest.raises(NotFoundError, match="does not exist"):
                await piglet.dns.edit("example.com", "123", ARecord(content="1.2.3.4"))
