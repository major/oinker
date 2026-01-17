"""Tests for DNS record dataclasses and validation."""

from __future__ import annotations

from contextlib import nullcontext

import pytest

from oinker import (
    DNS_RECORD_CLASSES,
    DNS_RECORD_TYPES,
    AAAARecord,
    ALIASRecord,
    ARecord,
    CAARecord,
    CNAMERecord,
    HTTPSRecord,
    MXRecord,
    NSRecord,
    SRVRecord,
    SSHFPRecord,
    SVCBRecord,
    TLSARecord,
    TXTRecord,
    ValidationError,
)
from oinker.dns._records import DNSRecordResponse


class TestARecord:
    """Tests for A record validation."""

    @pytest.mark.parametrize(
        ("content", "expected_valid"),
        [
            ("1.2.3.4", True),
            ("192.168.1.1", True),
            ("255.255.255.255", True),
            ("0.0.0.0", True),
            ("999.999.999.999", False),
            ("not-an-ip", False),
            ("1.2.3", False),
            ("1.2.3.4.5", False),
            ("2001:db8::1", False),
            ("", False),
        ],
    )
    def test_ipv4_validation(self, content: str, expected_valid: bool) -> None:
        expectation = nullcontext() if expected_valid else pytest.raises(ValidationError)
        with expectation:
            ARecord(content=content)

    def test_ttl_validation_minimum(self) -> None:
        with pytest.raises(ValidationError, match="at least 600"):
            ARecord(content="1.2.3.4", ttl=599)

    def test_defaults(self) -> None:
        record = ARecord(content="1.2.3.4")
        assert record.name is None
        assert record.ttl == 600
        assert record.notes is None
        assert record.record_type == "A"

    def test_ipv4_accepted(self) -> None:
        record = ARecord(content="192.168.1.1")
        assert record.content == "192.168.1.1"


class TestAAAARecord:
    """Tests for AAAA record validation."""

    @pytest.mark.parametrize(
        ("content", "expected_valid"),
        [
            ("2001:db8::1", True),
            ("::1", True),
            ("::", True),
            ("2001:0db8:0000:0000:0000:0000:0000:0001", True),
            ("fe80::1", True),
            ("1.2.3.4", False),
            ("not-an-ip", False),
            ("", False),
            ("2001:db8:::1", False),
        ],
    )
    def test_ipv6_validation(self, content: str, expected_valid: bool) -> None:
        expectation = nullcontext() if expected_valid else pytest.raises(ValidationError)
        with expectation:
            AAAARecord(content=content)

    def test_ip_normalization(self) -> None:
        record = AAAARecord(content="2001:0db8:0000:0000:0000:0000:0000:0001")
        assert record.content == "2001:db8::1"


class TestMXRecord:
    """Tests for MX record validation."""

    def test_valid_mx(self) -> None:
        record = MXRecord(content="mail.example.com", priority=10)
        assert record.content == "mail.example.com"
        assert record.priority == 10
        assert record.record_type == "MX"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            MXRecord(content="", priority=10)

    def test_negative_priority_fails(self) -> None:
        with pytest.raises(ValidationError, match="non-negative"):
            MXRecord(content="mail.example.com", priority=-1)

    def test_defaults(self) -> None:
        record = MXRecord(content="mail.example.com")
        assert record.priority == 10
        assert record.ttl == 600


class TestTXTRecord:
    """Tests for TXT record validation."""

    def test_valid_txt(self) -> None:
        record = TXTRecord(content="v=spf1 include:_spf.example.com ~all")
        assert record.content == "v=spf1 include:_spf.example.com ~all"
        assert record.record_type == "TXT"

    def test_empty_content_allowed(self) -> None:
        record = TXTRecord(content="")
        assert record.content == ""


class TestCNAMERecord:
    """Tests for CNAME record validation."""

    def test_valid_cname(self) -> None:
        record = CNAMERecord(content="example.com", name="www")
        assert record.content == "example.com"
        assert record.name == "www"
        assert record.record_type == "CNAME"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            CNAMERecord(content="")


class TestALIASRecord:
    """Tests for ALIAS record validation."""

    def test_valid_alias(self) -> None:
        record = ALIASRecord(content="example.com")
        assert record.content == "example.com"
        assert record.record_type == "ALIAS"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            ALIASRecord(content="")


class TestNSRecord:
    """Tests for NS record validation."""

    def test_valid_ns(self) -> None:
        record = NSRecord(content="ns1.example.com")
        assert record.content == "ns1.example.com"
        assert record.record_type == "NS"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            NSRecord(content="")


class TestSRVRecord:
    """Tests for SRV record validation."""

    def test_valid_srv(self) -> None:
        record = SRVRecord(content="5 5060 sipserver.example.com", priority=10, name="_sip._tcp")
        assert record.content == "5 5060 sipserver.example.com"
        assert record.priority == 10
        assert record.record_type == "SRV"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            SRVRecord(content="")


class TestTLSARecord:
    """Tests for TLSA record validation."""

    def test_valid_tlsa(self) -> None:
        record = TLSARecord(content="3 1 1 abc123", name="_443._tcp")
        assert record.content == "3 1 1 abc123"
        assert record.record_type == "TLSA"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            TLSARecord(content="")


class TestCAARecord:
    """Tests for CAA record validation."""

    def test_valid_caa(self) -> None:
        record = CAARecord(content='0 issue "letsencrypt.org"')
        assert record.content == '0 issue "letsencrypt.org"'
        assert record.record_type == "CAA"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            CAARecord(content="")


class TestHTTPSRecord:
    """Tests for HTTPS record validation."""

    def test_valid_https(self) -> None:
        record = HTTPSRecord(content='. alpn="h2,h3"', priority=1)
        assert record.content == '. alpn="h2,h3"'
        assert record.priority == 1
        assert record.record_type == "HTTPS"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            HTTPSRecord(content="")


class TestSVCBRecord:
    """Tests for SVCB record validation."""

    def test_valid_svcb(self) -> None:
        record = SVCBRecord(content=". port=443", priority=1)
        assert record.content == ". port=443"
        assert record.record_type == "SVCB"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            SVCBRecord(content="")


class TestSSHFPRecord:
    """Tests for SSHFP record validation."""

    def test_valid_sshfp(self) -> None:
        record = SSHFPRecord(content="1 1 abc123def456")
        assert record.content == "1 1 abc123def456"
        assert record.record_type == "SSHFP"

    def test_empty_content_fails(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            SSHFPRecord(content="")


class TestDNSRecordResponse:
    """Tests for DNS record response parsing."""

    def test_from_api_response(self) -> None:
        data = {
            "id": "123456",
            "name": "www.example.com",
            "type": "A",
            "content": "1.2.3.4",
            "ttl": "600",
            "prio": "0",
            "notes": "Test record",
        }
        record = DNSRecordResponse.from_api_response(data)
        assert record.id == "123456"
        assert record.name == "www.example.com"
        assert record.record_type == "A"
        assert record.content == "1.2.3.4"
        assert record.ttl == 600
        assert record.priority == 0
        assert record.notes == "Test record"

    def test_from_api_response_with_defaults(self) -> None:
        data = {"id": "123", "name": "example.com", "type": "TXT", "content": "test"}
        record = DNSRecordResponse.from_api_response(data)
        assert record.ttl == 600
        assert record.priority == 0
        assert record.notes == ""

    @pytest.mark.parametrize(
        ("ttl_value", "prio_value", "expected_ttl", "expected_prio"),
        [
            ("", "", 600, 0),
            ("abc", "xyz", 600, 0),
            ("300", "5", 300, 5),
            (None, None, 600, 0),
        ],
    )
    def test_from_api_response_malformed_integers(
        self, ttl_value: str | None, prio_value: str | None, expected_ttl: int, expected_prio: int
    ) -> None:
        data: dict[str, str] = {
            "id": "123",
            "name": "example.com",
            "type": "A",
            "content": "1.2.3.4",
        }
        if ttl_value is not None:
            data["ttl"] = ttl_value
        if prio_value is not None:
            data["prio"] = prio_value
        record = DNSRecordResponse.from_api_response(data)
        assert record.ttl == expected_ttl
        assert record.priority == expected_prio


class TestDNSRecordRegistry:
    EXPECTED_TYPES = frozenset(
        [
            "A",
            "AAAA",
            "MX",
            "CNAME",
            "ALIAS",
            "TXT",
            "NS",
            "SRV",
            "TLSA",
            "CAA",
            "HTTPS",
            "SVCB",
            "SSHFP",
        ]
    )

    def test_dns_record_types_contains_all_expected(self) -> None:
        assert DNS_RECORD_TYPES == self.EXPECTED_TYPES

    def test_dns_record_classes_keys_match_types(self) -> None:
        assert set(DNS_RECORD_CLASSES.keys()) == DNS_RECORD_TYPES

    def test_each_class_has_matching_record_type(self) -> None:
        for type_str, cls in DNS_RECORD_CLASSES.items():
            assert cls.record_type == type_str

    @pytest.mark.parametrize("record_type", list(EXPECTED_TYPES))
    def test_instantiation_via_registry(self, record_type: str) -> None:
        cls = DNS_RECORD_CLASSES[record_type]
        kwargs: dict[str, str | int] = {"content": "test.example.com", "ttl": 600}
        if hasattr(cls, "priority"):
            kwargs["priority"] = 10
        if record_type == "A":
            kwargs["content"] = "1.2.3.4"
        elif record_type == "AAAA":
            kwargs["content"] = "2001:db8::1"
        record = cls(**kwargs)
        assert record.record_type == record_type
