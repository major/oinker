"""Domain-related type definitions for oinker.

Dataclasses for domain operations like listing, nameservers, URL forwarding, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class DomainLabel:
    """A label attached to a domain.

    Attributes:
        id: The label ID.
        title: The label title.
        color: The label color (hex format).
    """

    id: str
    title: str
    color: str

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> DomainLabel:
        """Create from API response data.

        Args:
            data: The API response dictionary.

        Returns:
            A DomainLabel instance.
        """
        return cls(
            id=str(data.get("id", "")),
            title=data.get("title", ""),
            color=data.get("color", ""),
        )


@dataclass(frozen=True, slots=True)
class DomainInfo:
    """Information about a domain in the account.

    Attributes:
        domain: The domain name.
        status: The domain status (e.g., "ACTIVE").
        tld: The top-level domain.
        create_date: When the domain was created.
        expire_date: When the domain expires.
        security_lock: Whether security lock is enabled.
        whois_privacy: Whether WHOIS privacy is enabled.
        auto_renew: Whether auto-renew is enabled.
        not_local: Whether the domain is not local.
        labels: Labels attached to the domain.
    """

    domain: str
    status: str
    tld: str
    create_date: datetime | None
    expire_date: datetime | None
    security_lock: bool
    whois_privacy: bool
    auto_renew: bool
    not_local: bool
    labels: tuple[DomainLabel, ...]

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> DomainInfo:
        """Create from API response data.

        Args:
            data: The API response dictionary.

        Returns:
            A DomainInfo instance.
        """

        def parse_date(value: str | None) -> datetime | None:
            if not value:
                return None
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None

        labels_data = data.get("labels", [])
        labels = tuple(DomainLabel.from_api_response(lbl) for lbl in labels_data)

        return cls(
            domain=data.get("domain", ""),
            status=data.get("status", ""),
            tld=data.get("tld", ""),
            create_date=parse_date(data.get("createDate")),
            expire_date=parse_date(data.get("expireDate")),
            security_lock=data.get("securityLock") == "1" or data.get("securityLock") is True,
            whois_privacy=data.get("whoisPrivacy") == "1" or data.get("whoisPrivacy") is True,
            auto_renew=bool(data.get("autoRenew")),
            not_local=bool(data.get("notLocal")),
            labels=labels,
        )


URLForwardType = Literal["temporary", "permanent"]


@dataclass(frozen=True, slots=True)
class URLForward:
    """A URL forwarding rule for a domain.

    Attributes:
        id: The forward rule ID.
        subdomain: The subdomain being forwarded (empty for root).
        location: The destination URL.
        type: The redirect type ("temporary" or "permanent").
        include_path: Whether to include the URI path in redirection.
        wildcard: Whether to forward all subdomains.
    """

    id: str
    subdomain: str
    location: str
    type: URLForwardType
    include_path: bool
    wildcard: bool

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> URLForward:
        """Create from API response data.

        Args:
            data: The API response dictionary.

        Returns:
            A URLForward instance.
        """
        forward_type = data.get("type", "temporary")
        if forward_type not in ("temporary", "permanent"):
            forward_type = "temporary"

        return cls(
            id=str(data.get("id", "")),
            subdomain=data.get("subdomain", ""),
            location=data.get("location", ""),
            type=forward_type,
            include_path=data.get("includePath") == "yes",
            wildcard=data.get("wildcard") == "yes",
        )


@dataclass(slots=True)
class URLForwardCreate:
    """Parameters for creating a URL forward.

    Attributes:
        location: Where to forward the domain to.
        type: The redirect type ("temporary" or "permanent").
        subdomain: The subdomain to forward (None for root).
        include_path: Whether to include the URI path in redirection.
        wildcard: Whether to forward all subdomains.
    """

    location: str
    type: URLForwardType = "temporary"
    subdomain: str | None = None
    include_path: bool = False
    wildcard: bool = False


@dataclass(frozen=True, slots=True)
class GlueRecord:
    """A glue record (name server with IP addresses).

    Attributes:
        hostname: The full hostname (e.g., "ns1.example.com").
        ipv4: List of IPv4 addresses.
        ipv6: List of IPv6 addresses.
    """

    hostname: str
    ipv4: tuple[str, ...]
    ipv6: tuple[str, ...]

    @classmethod
    def from_api_response(cls, host_data: tuple[str, dict[str, Any]]) -> GlueRecord:
        """Create from API response data.

        The API returns glue records as a tuple of [hostname, {v4: [...], v6: [...]}].

        Args:
            host_data: The host data tuple from API response.

        Returns:
            A GlueRecord instance.
        """
        hostname, ips = host_data
        return cls(
            hostname=hostname,
            ipv4=tuple(ips.get("v4", [])),
            ipv6=tuple(ips.get("v6", [])),
        )


@dataclass(frozen=True, slots=True)
class DomainPricing:
    """Pricing information for a domain operation.

    Attributes:
        type: The operation type (registration, renewal, transfer).
        price: The current price.
        regular_price: The regular (non-promo) price.
    """

    type: str
    price: str
    regular_price: str


@dataclass(frozen=True, slots=True)
class DomainAvailability:
    """Domain availability check result.

    Attributes:
        available: Whether the domain is available for registration.
        type: The operation type (registration).
        price: The current price.
        regular_price: The regular (non-promo) price.
        first_year_promo: Whether first year promo pricing applies.
        premium: Whether this is a premium domain.
        renewal: Renewal pricing info.
        transfer: Transfer pricing info.
    """

    available: bool
    type: str
    price: str
    regular_price: str
    first_year_promo: bool
    premium: bool
    renewal: DomainPricing | None
    transfer: DomainPricing | None

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> DomainAvailability:
        """Create from API response data.

        Args:
            data: The "response" dictionary from API.

        Returns:
            A DomainAvailability instance.
        """
        additional = data.get("additional", {})
        renewal_data = additional.get("renewal")
        transfer_data = additional.get("transfer")

        renewal = None
        if renewal_data:
            renewal = DomainPricing(
                type=renewal_data.get("type", "renewal"),
                price=renewal_data.get("price", ""),
                regular_price=renewal_data.get("regularPrice", ""),
            )

        transfer = None
        if transfer_data:
            transfer = DomainPricing(
                type=transfer_data.get("type", "transfer"),
                price=transfer_data.get("price", ""),
                regular_price=transfer_data.get("regularPrice", ""),
            )

        return cls(
            available=data.get("avail") == "yes",
            type=data.get("type", ""),
            price=data.get("price", ""),
            regular_price=data.get("regularPrice", ""),
            first_year_promo=data.get("firstYearPromo") == "yes",
            premium=data.get("premium") == "yes",
            renewal=renewal,
            transfer=transfer,
        )
