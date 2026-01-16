"""Tests for domain dataclasses and type parsing."""

from __future__ import annotations

from oinker.domains import (
    DomainAvailability,
    DomainInfo,
    DomainLabel,
    DomainPricing,
    GlueRecord,
    URLForward,
    URLForwardCreate,
)


class TestDomainLabel:
    """Tests for DomainLabel dataclass."""

    def test_from_api_response(self) -> None:
        data = {"id": "27240", "title": "cool", "color": "#ff9e9e"}
        label = DomainLabel.from_api_response(data)
        assert label.id == "27240"
        assert label.title == "cool"
        assert label.color == "#ff9e9e"

    def test_from_api_response_missing_fields(self) -> None:
        data: dict[str, str] = {}
        label = DomainLabel.from_api_response(data)
        assert label.id == ""
        assert label.title == ""
        assert label.color == ""


class TestDomainInfo:
    """Tests for DomainInfo dataclass."""

    def test_from_api_response_full(self) -> None:
        data = {
            "domain": "example.com",
            "status": "ACTIVE",
            "tld": "com",
            "createDate": "2018-08-20 17:52:51",
            "expireDate": "2023-08-20 17:52:51",
            "securityLock": "1",
            "whoisPrivacy": "1",
            "autoRenew": 1,
            "notLocal": 0,
            "labels": [
                {"id": "27240", "title": "cool", "color": "#ff9e9e"},
                {"id": "27241", "title": "silly", "color": "#f00000"},
            ],
        }
        info = DomainInfo.from_api_response(data)
        assert info.domain == "example.com"
        assert info.status == "ACTIVE"
        assert info.tld == "com"
        assert info.create_date is not None
        assert info.create_date.year == 2018
        assert info.expire_date is not None
        assert info.expire_date.year == 2023
        assert info.security_lock is True
        assert info.whois_privacy is True
        assert info.auto_renew is True
        assert info.not_local is False
        assert len(info.labels) == 2
        assert info.labels[0].title == "cool"

    def test_from_api_response_minimal(self) -> None:
        data = {"domain": "test.io", "status": "ACTIVE", "tld": "io"}
        info = DomainInfo.from_api_response(data)
        assert info.domain == "test.io"
        assert info.create_date is None
        assert info.expire_date is None
        assert info.security_lock is False
        assert info.labels == ()

    def test_from_api_response_bool_security_lock(self) -> None:
        data = {"domain": "test.io", "securityLock": True, "whoisPrivacy": False}
        info = DomainInfo.from_api_response(data)
        assert info.security_lock is True
        assert info.whois_privacy is False

    def test_from_api_response_invalid_date(self) -> None:
        data = {"domain": "test.io", "createDate": "not-a-date"}
        info = DomainInfo.from_api_response(data)
        assert info.create_date is None


class TestURLForward:
    """Tests for URLForward dataclass."""

    def test_from_api_response(self) -> None:
        data = {
            "id": "22049216",
            "subdomain": "",
            "location": "https://porkbun.com",
            "type": "temporary",
            "includePath": "no",
            "wildcard": "yes",
        }
        forward = URLForward.from_api_response(data)
        assert forward.id == "22049216"
        assert forward.subdomain == ""
        assert forward.location == "https://porkbun.com"
        assert forward.type == "temporary"
        assert forward.include_path is False
        assert forward.wildcard is True

    def test_from_api_response_permanent(self) -> None:
        data = {
            "id": "123",
            "subdomain": "blog",
            "location": "https://blog.example.com",
            "type": "permanent",
            "includePath": "yes",
            "wildcard": "no",
        }
        forward = URLForward.from_api_response(data)
        assert forward.type == "permanent"
        assert forward.include_path is True
        assert forward.wildcard is False

    def test_from_api_response_invalid_type_defaults_to_temporary(self) -> None:
        data = {
            "id": "123",
            "location": "https://example.com",
            "type": "invalid_type",
        }
        forward = URLForward.from_api_response(data)
        assert forward.type == "temporary"


class TestURLForwardCreate:
    """Tests for URLForwardCreate dataclass."""

    def test_defaults(self) -> None:
        forward = URLForwardCreate(location="https://example.com")
        assert forward.location == "https://example.com"
        assert forward.type == "temporary"
        assert forward.subdomain is None
        assert forward.include_path is False
        assert forward.wildcard is False

    def test_all_fields(self) -> None:
        forward = URLForwardCreate(
            location="https://example.com",
            type="permanent",
            subdomain="blog",
            include_path=True,
            wildcard=True,
        )
        assert forward.type == "permanent"
        assert forward.subdomain == "blog"
        assert forward.include_path is True


class TestGlueRecord:
    """Tests for GlueRecord dataclass."""

    def test_from_api_response(self) -> None:
        host_data = (
            "ns1.example.com",
            {
                "v4": ["192.168.1.1", "192.168.1.2"],
                "v6": ["2001:db8::1"],
            },
        )
        glue = GlueRecord.from_api_response(host_data)
        assert glue.hostname == "ns1.example.com"
        assert glue.ipv4 == ("192.168.1.1", "192.168.1.2")
        assert glue.ipv6 == ("2001:db8::1",)

    def test_from_api_response_empty_ips(self) -> None:
        host_data = ("ns1.example.com", {})
        glue = GlueRecord.from_api_response(host_data)
        assert glue.ipv4 == ()
        assert glue.ipv6 == ()


class TestDomainPricing:
    """Tests for DomainPricing dataclass."""

    def test_creation(self) -> None:
        pricing = DomainPricing(type="renewal", price="9.68", regular_price="11.82")
        assert pricing.type == "renewal"
        assert pricing.price == "9.68"
        assert pricing.regular_price == "11.82"


class TestDomainAvailability:
    """Tests for DomainAvailability dataclass."""

    def test_from_api_response_available(self) -> None:
        data = {
            "avail": "yes",
            "type": "registration",
            "price": "1.01",
            "regularPrice": "11.82",
            "firstYearPromo": "yes",
            "premium": "no",
            "additional": {
                "renewal": {"type": "renewal", "price": "11.82", "regularPrice": "11.82"},
                "transfer": {"type": "transfer", "price": "11.82", "regularPrice": "11.82"},
            },
        }
        avail = DomainAvailability.from_api_response(data)
        assert avail.available is True
        assert avail.type == "registration"
        assert avail.price == "1.01"
        assert avail.first_year_promo is True
        assert avail.premium is False
        assert avail.renewal is not None
        assert avail.renewal.price == "11.82"
        assert avail.transfer is not None
        assert avail.transfer.type == "transfer"

    def test_from_api_response_unavailable(self) -> None:
        data = {
            "avail": "no",
            "type": "registration",
            "price": "11.82",
            "regularPrice": "11.82",
            "firstYearPromo": "no",
            "premium": "no",
        }
        avail = DomainAvailability.from_api_response(data)
        assert avail.available is False
        assert avail.first_year_promo is False
        assert avail.renewal is None
        assert avail.transfer is None

    def test_from_api_response_premium(self) -> None:
        data = {
            "avail": "yes",
            "type": "registration",
            "price": "999.99",
            "regularPrice": "999.99",
            "premium": "yes",
        }
        avail = DomainAvailability.from_api_response(data)
        assert avail.premium is True
