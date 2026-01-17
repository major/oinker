"""DNS record dataclasses with validation.

Type-safe representations of DNS records supported by the Porkbun API.
All records validate their content on initialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import AddressValueError, IPv4Address, IPv6Address
from typing import ClassVar, Literal

from oinker._exceptions import ValidationError

# Valid DNS record types supported by Porkbun API
DNSRecordType = Literal[
    "A", "AAAA", "MX", "CNAME", "ALIAS", "TXT", "NS", "SRV", "TLSA", "CAA", "HTTPS", "SVCB", "SSHFP"
]


def _validate_ipv4(value: str) -> IPv4Address:
    """Validate and parse an IPv4 address.

    Args:
        value: String representation of IPv4 address.

    Returns:
        Parsed IPv4Address object.

    Raises:
        ValidationError: If the value is not a valid IPv4 address.
    """
    try:
        return IPv4Address(value)
    except AddressValueError as e:
        msg = f"Invalid IPv4 address: {value}"
        raise ValidationError(msg) from e


def _validate_ipv6(value: str) -> IPv6Address:
    """Validate and parse an IPv6 address.

    Args:
        value: String representation of IPv6 address.

    Returns:
        Parsed IPv6Address object.

    Raises:
        ValidationError: If the value is not a valid IPv6 address.
    """
    try:
        return IPv6Address(value)
    except AddressValueError as e:
        msg = f"Invalid IPv6 address: {value}"
        raise ValidationError(msg) from e


def _validate_ttl(ttl: int) -> None:
    """Validate TTL is at least the minimum (600 seconds).

    Args:
        ttl: Time to live in seconds.

    Raises:
        ValidationError: If TTL is below minimum.
    """
    if ttl < 600:
        msg = f"TTL must be at least 600 seconds, got {ttl}"
        raise ValidationError(msg)


def _validate_priority(priority: int) -> None:
    """Validate priority is non-negative.

    Args:
        priority: Priority value.

    Raises:
        ValidationError: If priority is negative.
    """
    if priority < 0:
        msg = f"Priority must be non-negative, got {priority}"
        raise ValidationError(msg)


def _validate_content_not_empty(
    content: str, record_type: str, description: str | None = None
) -> None:
    """Validate that content is not empty.

    Args:
        content: The record content.
        record_type: The record type name for error message.
        description: Optional human-readable description of the content
            (e.g., "mail server", "target", "nameserver") to include in
            the error message.

    Raises:
        ValidationError: If content is empty.
    """
    if not content:
        if description:
            msg = f"{record_type} record content ({description}) cannot be empty"
        else:
            msg = f"{record_type} record content cannot be empty"
        raise ValidationError(msg)


def _safe_int(value: str, default: int) -> int:
    """Safely parse a string to int with fallback.

    Args:
        value: String to parse.
        default: Default value if parsing fails.

    Returns:
        Parsed integer or default.
    """
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(slots=True)
class ARecord:
    """A record pointing to an IPv4 address.

    Attributes:
        content: IPv4 address (validated on init).
        name: Subdomain (None = root domain, "*" = wildcard).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "A"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record content."""
        # Validate and normalize the IP address
        ip = _validate_ipv4(self.content)
        object.__setattr__(self, "content", str(ip))
        _validate_ttl(self.ttl)


@dataclass(slots=True)
class AAAARecord:
    """AAAA record pointing to an IPv6 address.

    Attributes:
        content: IPv6 address (validated on init).
        name: Subdomain (None = root domain, "*" = wildcard).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "AAAA"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record content."""
        ip = _validate_ipv6(self.content)
        object.__setattr__(self, "content", str(ip))
        _validate_ttl(self.ttl)


@dataclass(slots=True)
class MXRecord:
    """MX record for mail servers.

    Attributes:
        content: Mail server hostname.
        priority: Mail priority (lower = higher priority).
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "MX"

    content: str
    priority: int = 10
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_priority(self.priority)
        _validate_content_not_empty(self.content, "MX", "mail server")


@dataclass(slots=True)
class TXTRecord:
    """TXT record for arbitrary text data.

    Attributes:
        content: Text content.
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "TXT"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)


@dataclass(slots=True)
class CNAMERecord:
    """CNAME record pointing to another hostname.

    Attributes:
        content: Target hostname.
        name: Subdomain (None allowed, but may be rejected by API for root CNAMEs).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "CNAME"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_content_not_empty(self.content, "CNAME", "target")


@dataclass(slots=True)
class ALIASRecord:
    """ALIAS record (ANAME) for root domain CNAME-like behavior.

    Attributes:
        content: Target hostname.
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "ALIAS"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_content_not_empty(self.content, "ALIAS", "target")


@dataclass(slots=True)
class NSRecord:
    """NS record delegating to a name server.

    Attributes:
        content: Nameserver hostname.
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "NS"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_content_not_empty(self.content, "NS", "nameserver")


@dataclass(slots=True)
class SRVRecord:
    """SRV record for service discovery.

    Content format: "weight port target" (e.g., "5 5060 sipserver.example.com")

    Attributes:
        content: SRV data in "weight port target" format.
        priority: Service priority (lower = higher priority).
        name: Service name (e.g., "_sip._tcp").
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "SRV"

    content: str
    priority: int = 10
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_priority(self.priority)
        _validate_content_not_empty(self.content, "SRV")


@dataclass(slots=True)
class TLSARecord:
    """TLSA record for DANE TLS authentication.

    Content format: "usage selector matching_type certificate_data"

    Attributes:
        content: TLSA data.
        name: Port and protocol prefix (e.g., "_443._tcp").
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "TLSA"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_content_not_empty(self.content, "TLSA")


@dataclass(slots=True)
class CAARecord:
    """CAA record for certificate authority authorization.

    Content format: 'flags tag "value"' (e.g., '0 issue "letsencrypt.org"')

    Attributes:
        content: CAA data.
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "CAA"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_content_not_empty(self.content, "CAA")


@dataclass(slots=True)
class HTTPSRecord:
    """HTTPS record for service binding.

    Attributes:
        content: HTTPS SVCB data.
        priority: Priority (0 = alias mode).
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "HTTPS"

    content: str
    priority: int = 1
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_priority(self.priority)
        _validate_content_not_empty(self.content, "HTTPS")


@dataclass(slots=True)
class SVCBRecord:
    """SVCB record for general service binding.

    Attributes:
        content: SVCB data.
        priority: Priority (0 = alias mode).
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "SVCB"

    content: str
    priority: int = 1
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_priority(self.priority)
        _validate_content_not_empty(self.content, "SVCB")


@dataclass(slots=True)
class SSHFPRecord:
    """SSHFP record for SSH fingerprint verification.

    Content format: "algorithm fingerprint_type fingerprint"

    Attributes:
        content: SSHFP data.
        name: Subdomain (None = root domain).
        ttl: Time to live in seconds (min 600).
        notes: Optional notes for the record.
    """

    record_type: ClassVar[DNSRecordType] = "SSHFP"

    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the record."""
        _validate_ttl(self.ttl)
        _validate_content_not_empty(self.content, "SSHFP")


# Type alias for any DNS record
DNSRecord = (
    ARecord
    | AAAARecord
    | MXRecord
    | TXTRecord
    | CNAMERecord
    | ALIASRecord
    | NSRecord
    | SRVRecord
    | TLSARecord
    | CAARecord
    | HTTPSRecord
    | SVCBRecord
    | SSHFPRecord
)


@dataclass(frozen=True, slots=True)
class DNSRecordResponse:
    """A DNS record as returned from the API.

    Attributes:
        id: Unique record identifier.
        name: Full domain name (e.g., "www.example.com").
        record_type: DNS record type (A, AAAA, etc.).
        content: Record content/answer.
        ttl: Time to live in seconds.
        priority: Record priority (for MX, SRV, etc.).
        notes: Optional notes.
    """

    id: str
    name: str
    record_type: str
    content: str
    ttl: int
    priority: int = 0
    notes: str = ""

    @classmethod
    def from_api_response(cls, data: dict[str, str]) -> DNSRecordResponse:
        """Create a DNSRecordResponse from API response data.

        Args:
            data: Dictionary from Porkbun API.

        Returns:
            Parsed DNSRecordResponse.
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            record_type=data.get("type", ""),
            content=data.get("content", ""),
            ttl=_safe_int(data.get("ttl", ""), 600),
            priority=_safe_int(data.get("prio", ""), 0),
            notes=data.get("notes", ""),
        )
