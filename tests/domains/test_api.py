"""Tests for async Domain API operations."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from oinker import AsyncPiglet, Piglet
from oinker._config import OinkerConfig
from oinker.domains import URLForwardCreate

from tests.conftest import make_response


class TestAsyncDomainsAPIList:
    """Tests for domains.list() operation."""

    async def test_list_domains_success(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "domains": [
                    {
                        "domain": "example.com",
                        "status": "ACTIVE",
                        "tld": "com",
                        "createDate": "2018-08-20 17:52:51",
                        "expireDate": "2023-08-20 17:52:51",
                        "securityLock": "1",
                        "whoisPrivacy": "1",
                        "autoRenew": 0,
                        "notLocal": 0,
                    }
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            domains = await piglet.domains.list()

        assert len(domains) == 1
        assert domains[0].domain == "example.com"
        assert domains[0].status == "ACTIVE"

    async def test_list_with_pagination(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "domains": []})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.list(start=1000)

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("start") == "1000"

    async def test_list_with_labels(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "domains": []})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.list(include_labels=True)

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("includeLabels") == "yes"


class TestAsyncDomainsAPINameservers:
    """Tests for nameserver operations."""

    async def test_get_nameservers(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "ns": [
                    "curitiba.ns.porkbun.com",
                    "fortaleza.ns.porkbun.com",
                    "maceio.ns.porkbun.com",
                    "salvador.ns.porkbun.com",
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            ns = await piglet.domains.get_nameservers("example.com")

        assert len(ns) == 4
        assert "curitiba.ns.porkbun.com" in ns
        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/getNs/example.com"

    async def test_update_nameservers(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.update_nameservers(
                "example.com", ["ns1.example.com", "ns2.example.com"]
            )

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/updateNs/example.com"
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("ns") == ["ns1.example.com", "ns2.example.com"]


class TestAsyncDomainsAPIURLForwarding:
    """Tests for URL forwarding operations."""

    async def test_get_url_forwards(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "forwards": [
                    {
                        "id": "22049216",
                        "subdomain": "",
                        "location": "https://porkbun.com",
                        "type": "temporary",
                        "includePath": "no",
                        "wildcard": "yes",
                    },
                    {
                        "id": "22049209",
                        "subdomain": "blog",
                        "location": "https://blog.porkbun.com",
                        "type": "temporary",
                        "includePath": "no",
                        "wildcard": "yes",
                    },
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            forwards = await piglet.domains.get_url_forwards("example.com")

        assert len(forwards) == 2
        assert forwards[0].location == "https://porkbun.com"
        assert forwards[1].subdomain == "blog"

    async def test_add_url_forward(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        forward = URLForwardCreate(
            location="https://porkbun.com",
            type="temporary",
            subdomain="blog",
            include_path=True,
            wildcard=True,
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.add_url_forward("example.com", forward)

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/addUrlForward/example.com"
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("location") == "https://porkbun.com"
        assert request_json.get("type") == "temporary"
        assert request_json.get("subdomain") == "blog"
        assert request_json.get("includePath") == "yes"
        assert request_json.get("wildcard") == "yes"

    async def test_add_url_forward_root_domain(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        forward = URLForwardCreate(location="https://example.com")

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.add_url_forward("example.com", forward)

        call_args = mock_httpx_client.post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("subdomain") == ""

    async def test_delete_url_forward(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.delete_url_forward("example.com", "22049209")

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/deleteUrlForward/example.com/22049209"


class TestAsyncDomainsAPIDomainCheck:
    """Tests for domain availability check."""

    async def test_check_domain(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "response": {
                    "avail": "no",
                    "type": "registration",
                    "price": "1.01",
                    "regularPrice": "11.82",
                    "firstYearPromo": "yes",
                    "premium": "no",
                    "additional": {
                        "renewal": {"type": "renewal", "price": "11.82", "regularPrice": "11.82"},
                        "transfer": {"type": "transfer", "price": "11.82", "regularPrice": "11.82"},
                    },
                },
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            avail = await piglet.domains.check("example.com")

        assert avail.available is False
        assert avail.first_year_promo is True
        assert avail.renewal is not None
        assert avail.renewal.price == "11.82"
        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/checkDomain/example.com"


class TestAsyncDomainsAPIGlueRecords:
    """Tests for glue record operations."""

    async def test_get_glue_records(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "hosts": [
                    [
                        "ns1.example.com",
                        {"v6": ["2001:db8::1"], "v4": ["192.168.1.1"]},
                    ],
                    [
                        "ns2.example.com",
                        {"v6": ["2001:db8::2"], "v4": ["192.168.1.2"]},
                    ],
                ],
            }
        )

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            glue = await piglet.domains.get_glue_records("example.com")

        assert len(glue) == 2
        assert glue[0].hostname == "ns1.example.com"
        assert glue[0].ipv4 == ("192.168.1.1",)
        assert glue[0].ipv6 == ("2001:db8::1",)
        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/getGlue/example.com"

    async def test_create_glue_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.create_glue_record(
                "example.com", "ns1", ["192.168.1.1", "2001:db8::1"]
            )

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/createGlue/example.com/ns1"
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("ips") == ["192.168.1.1", "2001:db8::1"]

    async def test_update_glue_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.update_glue_record("example.com", "ns1", ["10.0.0.1"])

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/updateGlue/example.com/ns1"

    async def test_delete_glue_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        async with AsyncPiglet(
            api_key=config.api_key,
            secret_key=config.secret_key,
            _http_client=mock_httpx_client,
        ) as piglet:
            await piglet.domains.delete_glue_record("example.com", "ns1")

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/deleteGlue/example.com/ns1"


class TestSyncDomainsAPI:
    """Tests for sync Domains API wrapper."""

    def test_sync_list_domains(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "domains": [
                    {
                        "domain": "test.com",
                        "status": "ACTIVE",
                        "tld": "com",
                    }
                ],
            }
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            domains = piglet.domains.list()

        assert len(domains) == 1
        assert domains[0].domain == "test.com"

    def test_sync_get_nameservers(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {"status": "SUCCESS", "ns": ["ns1.example.com"]}
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            ns = piglet.domains.get_nameservers("example.com")

        assert ns == ["ns1.example.com"]

    def test_sync_update_nameservers(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.domains.update_nameservers("example.com", ["ns1.new.com", "ns2.new.com"])

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/updateNs/example.com"

    def test_sync_get_url_forwards(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "forwards": []})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            forwards = piglet.domains.get_url_forwards("example.com")

        assert forwards == []

    def test_sync_add_url_forward(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.domains.add_url_forward(
                "example.com",
                URLForwardCreate(location="https://test.com"),
            )

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/addUrlForward/example.com"

    def test_sync_delete_url_forward(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.domains.delete_url_forward("example.com", "123")

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/deleteUrlForward/example.com/123"

    def test_sync_check_domain(self, mock_httpx_client: AsyncMock, config: OinkerConfig) -> None:
        mock_httpx_client.post.return_value = make_response(
            {
                "status": "SUCCESS",
                "response": {"avail": "yes", "type": "registration", "price": "10.00"},
            }
        )

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            avail = piglet.domains.check("newdomain.com")

        assert avail.available is True

    def test_sync_get_glue_records(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS", "hosts": []})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            glue = piglet.domains.get_glue_records("example.com")

        assert glue == []

    def test_sync_create_glue_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.domains.create_glue_record("example.com", "ns1", ["1.2.3.4"])

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/createGlue/example.com/ns1"

    def test_sync_update_glue_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.domains.update_glue_record("example.com", "ns1", ["5.6.7.8"])

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/updateGlue/example.com/ns1"

    def test_sync_delete_glue_record(
        self, mock_httpx_client: AsyncMock, config: OinkerConfig
    ) -> None:
        mock_httpx_client.post.return_value = make_response({"status": "SUCCESS"})

        with Piglet(
            api_key=config.api_key, secret_key=config.secret_key, _http_client=mock_httpx_client
        ) as piglet:
            piglet.domains.delete_glue_record("example.com", "ns1")

        call_args = mock_httpx_client.post.call_args
        assert call_args.args[0] == "/domain/deleteGlue/example.com/ns1"
