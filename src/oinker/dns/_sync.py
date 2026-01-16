"""Synchronous DNS API wrapper.

Provides sync wrappers around the async DNS API.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from oinker.dns._records import DNSRecord, DNSRecordResponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from oinker.dns._api import AsyncDNSAPI


class SyncDNSAPI:
    """Synchronous DNS operations for the Porkbun API.

    Accessed via `piglet.dns.*` methods.
    """

    def __init__(
        self,
        async_api: AsyncDNSAPI,
        runner: Callable[..., Any],
    ) -> None:
        """Initialize sync DNS API."""
        self._async_api = async_api
        self._run = runner

    def list(self, domain: str) -> builtins.list[DNSRecordResponse]:
        """See :meth:`AsyncDNSAPI.list`."""
        return self._run(self._async_api.list(domain))

    def get(self, domain: str, record_id: str) -> DNSRecordResponse | None:
        """See :meth:`AsyncDNSAPI.get`."""
        return self._run(self._async_api.get(domain, record_id))

    def get_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str | None = None,
    ) -> builtins.list[DNSRecordResponse]:
        """See :meth:`AsyncDNSAPI.get_by_name_type`."""
        return self._run(self._async_api.get_by_name_type(domain, record_type, subdomain))

    def create(self, domain: str, record: DNSRecord) -> str:
        """See :meth:`AsyncDNSAPI.create`."""
        return self._run(self._async_api.create(domain, record))

    def edit(self, domain: str, record_id: str, record: DNSRecord) -> None:
        """See :meth:`AsyncDNSAPI.edit`."""
        self._run(self._async_api.edit(domain, record_id, record))

    def edit_by_name_type(
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
        """See :meth:`AsyncDNSAPI.edit_by_name_type`."""
        self._run(
            self._async_api.edit_by_name_type(
                domain,
                record_type,
                subdomain,
                content=content,
                ttl=ttl,
                priority=priority,
                notes=notes,
            )
        )

    def delete(self, domain: str, record_id: str) -> None:
        """See :meth:`AsyncDNSAPI.delete`."""
        self._run(self._async_api.delete(domain, record_id))

    def delete_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str | None = None,
    ) -> None:
        """See :meth:`AsyncDNSAPI.delete_by_name_type`."""
        self._run(self._async_api.delete_by_name_type(domain, record_type, subdomain))
