"""Async Domain API operations for the Porkbun API.

Provides domain management operations including nameservers, URL forwarding, and glue records.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from oinker.domains._types import (
    DomainAvailability,
    DomainInfo,
    GlueRecord,
    URLForward,
    URLForwardCreate,
)

if TYPE_CHECKING:
    from oinker._http import HttpClient


class AsyncDomainsAPI:
    """Async domain operations for the Porkbun API.

    Accessed via `piglet.domains.*` methods.
    """

    def __init__(self, http: HttpClient) -> None:
        """Initialize Domains API.

        Args:
            http: The HTTP client for making requests.
        """
        self._http = http

    async def list(
        self,
        start: int = 0,
        include_labels: bool = False,
    ) -> builtins.list[DomainInfo]:
        """List all domains in the account.

        Domains are returned in chunks of 1000. Increment start by 1000 until
        you receive an empty list to get all domains.

        Args:
            start: Index to start from (default 0).
            include_labels: Whether to include label info (default False).

        Returns:
            List of domain info objects.

        Raises:
            AuthenticationError: If credentials are invalid.
            APIError: If the request fails.
        """
        body: dict[str, Any] = {"start": str(start)}
        if include_labels:
            body["includeLabels"] = "yes"

        data = await self._http.post("/domain/listAll", body)
        domains = data.get("domains", [])
        return [DomainInfo.from_api_response(d) for d in domains]

    async def get_nameservers(self, domain: str) -> builtins.list[str]:
        """Get the authoritative nameservers for a domain.

        Args:
            domain: The domain name (e.g., "example.com").

        Returns:
            List of nameserver hostnames.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/domain/getNs/{domain}")
        return data.get("ns", [])

    async def update_nameservers(
        self,
        domain: str,
        nameservers: builtins.list[str],
    ) -> None:
        """Update the nameservers for a domain.

        Args:
            domain: The domain name (e.g., "example.com").
            nameservers: List of nameserver hostnames.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        await self._http.post(f"/domain/updateNs/{domain}", {"ns": nameservers})

    async def get_url_forwards(self, domain: str) -> builtins.list[URLForward]:
        """Get URL forwarding rules for a domain.

        Args:
            domain: The domain name (e.g., "example.com").

        Returns:
            List of URL forwarding rules.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/domain/getUrlForwarding/{domain}")
        forwards = data.get("forwards", [])
        return [URLForward.from_api_response(f) for f in forwards]

    async def add_url_forward(self, domain: str, forward: URLForwardCreate) -> None:
        """Add a URL forwarding rule for a domain.

        Args:
            domain: The domain name (e.g., "example.com").
            forward: The URL forward configuration.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        body: dict[str, Any] = {
            "location": forward.location,
            "type": forward.type,
            "includePath": "yes" if forward.include_path else "no",
            "wildcard": "yes" if forward.wildcard else "no",
        }
        if forward.subdomain is not None:
            body["subdomain"] = forward.subdomain
        else:
            body["subdomain"] = ""

        await self._http.post(f"/domain/addUrlForward/{domain}", body)

    async def delete_url_forward(self, domain: str, forward_id: str) -> None:
        """Delete a URL forwarding rule.

        Args:
            domain: The domain name (e.g., "example.com").
            forward_id: The forwarding rule ID to delete.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain or forward is not found.
            APIError: If the request fails.
        """
        await self._http.post(f"/domain/deleteUrlForward/{domain}/{forward_id}")

    async def check(self, domain: str) -> DomainAvailability:
        """Check a domain's availability.

        Note: Domain checks are rate limited.

        Args:
            domain: The domain name to check (e.g., "example.com").

        Returns:
            Domain availability information including pricing.

        Raises:
            AuthenticationError: If credentials are invalid.
            RateLimitError: If rate limit exceeded.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/domain/checkDomain/{domain}")
        return DomainAvailability.from_api_response(data.get("response", {}))

    async def get_glue_records(self, domain: str) -> builtins.list[GlueRecord]:
        """Get glue records for a domain.

        Args:
            domain: The domain name (e.g., "example.com").

        Returns:
            List of glue records.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/domain/getGlue/{domain}")
        hosts = data.get("hosts", [])
        return [GlueRecord.from_api_response(tuple(h)) for h in hosts]

    async def create_glue_record(
        self,
        domain: str,
        subdomain: str,
        ips: builtins.list[str],
    ) -> None:
        """Create a glue record for a domain.

        Args:
            domain: The domain name (e.g., "example.com").
            subdomain: The glue host subdomain (e.g., "ns1").
            ips: List of IP addresses (IPv4 and/or IPv6).

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        await self._http.post(
            f"/domain/createGlue/{domain}/{subdomain}",
            {"ips": ips},
        )

    async def update_glue_record(
        self,
        domain: str,
        subdomain: str,
        ips: builtins.list[str],
    ) -> None:
        """Update a glue record for a domain.

        Replaces all existing IP addresses with the new list.

        Args:
            domain: The domain name (e.g., "example.com").
            subdomain: The glue host subdomain (e.g., "ns1").
            ips: List of IP addresses (IPv4 and/or IPv6).

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain or glue record is not found.
            APIError: If the request fails.
        """
        await self._http.post(
            f"/domain/updateGlue/{domain}/{subdomain}",
            {"ips": ips},
        )

    async def delete_glue_record(self, domain: str, subdomain: str) -> None:
        """Delete a glue record for a domain.

        Args:
            domain: The domain name (e.g., "example.com").
            subdomain: The glue host subdomain (e.g., "ns1").

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain or glue record is not found.
            APIError: If the request fails.
        """
        await self._http.post(f"/domain/deleteGlue/{domain}/{subdomain}")
