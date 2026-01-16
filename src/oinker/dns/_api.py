"""Async DNS API operations for the Porkbun API.

Provides all DNS record management operations.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from oinker.dns._records import DNSRecord, DNSRecordResponse

if TYPE_CHECKING:
    from oinker._http import HttpClient


class AsyncDNSAPI:
    """Async DNS operations for the Porkbun API.

    Accessed via `piglet.dns.*` methods.
    """

    def __init__(self, http: HttpClient) -> None:
        """Initialize DNS API.

        Args:
            http: The HTTP client for making requests.
        """
        self._http = http

    async def list(self, domain: str) -> builtins.list[DNSRecordResponse]:
        """List all DNS records for a domain.

        Args:
            domain: The domain name (e.g., "example.com").

        Returns:
            List of DNS records.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/dns/retrieve/{domain}")
        records = data.get("records", [])
        return [DNSRecordResponse.from_api_response(r) for r in records]

    async def get(self, domain: str, record_id: str) -> DNSRecordResponse | None:
        """Get a specific DNS record by ID.

        Args:
            domain: The domain name.
            record_id: The record ID.

        Returns:
            The DNS record, or None if not found.

        Raises:
            AuthenticationError: If credentials are invalid.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/dns/retrieve/{domain}/{record_id}")
        records = data.get("records", [])
        if records:
            return DNSRecordResponse.from_api_response(records[0])
        return None

    async def get_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str | None = None,
    ) -> builtins.list[DNSRecordResponse]:
        """Get DNS records by subdomain and type.

        Args:
            domain: The domain name.
            record_type: The record type (A, AAAA, MX, etc.).
            subdomain: The subdomain (None for root).

        Returns:
            List of matching DNS records.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If no records match.
            APIError: If the request fails.
        """
        endpoint = f"/dns/retrieveByNameType/{domain}/{record_type}"
        if subdomain:
            endpoint = f"{endpoint}/{subdomain}"
        data = await self._http.post(endpoint)
        records = data.get("records", [])
        return [DNSRecordResponse.from_api_response(r) for r in records]

    async def create(self, domain: str, record: DNSRecord) -> str:
        """Create a new DNS record.

        Args:
            domain: The domain name.
            record: The DNS record to create.

        Returns:
            The ID of the created record.

        Raises:
            AuthenticationError: If credentials are invalid.
            ValidationError: If record data is invalid.
            APIError: If the request fails.
        """
        body = self._record_to_api_body(record)
        data = await self._http.post(f"/dns/create/{domain}", body)
        return str(data.get("id", ""))

    async def edit(self, domain: str, record_id: str, record: DNSRecord) -> None:
        """Edit an existing DNS record by ID.

        Args:
            domain: The domain name.
            record_id: The record ID to edit.
            record: The new record data.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If record is not found.
            ValidationError: If record data is invalid.
            APIError: If the request fails.
        """
        body = self._record_to_api_body(record)
        await self._http.post(f"/dns/edit/{domain}/{record_id}", body)

    async def edit_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str | None = None,
        *,
        content: str,
        ttl: int | None = None,
        priority: int | None = None,
        notes: str | None = None,
    ) -> None:
        """Edit all records matching subdomain and type.

        Args:
            domain: The domain name.
            record_type: The record type (A, AAAA, MX, etc.).
            subdomain: The subdomain (None for root).
            content: The new content value.
            ttl: Optional new TTL.
            priority: Optional new priority.
            notes: Optional new notes (empty string clears, None leaves unchanged).

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If no records match.
            APIError: If the request fails.
        """
        endpoint = f"/dns/editByNameType/{domain}/{record_type}"
        if subdomain:
            endpoint = f"{endpoint}/{subdomain}"

        body: dict[str, Any] = {"content": content}
        if ttl is not None:
            body["ttl"] = str(ttl)
        if priority is not None:
            body["prio"] = str(priority)
        if notes is not None:
            body["notes"] = notes

        await self._http.post(endpoint, body)

    async def delete(self, domain: str, record_id: str) -> None:
        """Delete a DNS record by ID.

        Args:
            domain: The domain name.
            record_id: The record ID to delete.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If record is not found.
            APIError: If the request fails.
        """
        await self._http.post(f"/dns/delete/{domain}/{record_id}")

    async def delete_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str | None = None,
    ) -> None:
        """Delete all records matching subdomain and type.

        Args:
            domain: The domain name.
            record_type: The record type (A, AAAA, MX, etc.).
            subdomain: The subdomain (None for root).

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If no records match.
            APIError: If the request fails.
        """
        endpoint = f"/dns/deleteByNameType/{domain}/{record_type}"
        if subdomain:
            endpoint = f"{endpoint}/{subdomain}"
        await self._http.post(endpoint)

    def _record_to_api_body(self, record: DNSRecord) -> dict[str, Any]:
        """Convert a DNS record to API request body.

        Args:
            record: The DNS record.

        Returns:
            Dictionary suitable for API request.
        """
        body: dict[str, Any] = {
            "type": record.record_type,
            "content": record.content,
            "ttl": str(record.ttl),
        }

        if record.name is not None:
            body["name"] = record.name

        if record.notes is not None:
            body["notes"] = record.notes

        priority = getattr(record, "priority", None)
        if priority is not None:
            body["prio"] = str(priority)

        return body
