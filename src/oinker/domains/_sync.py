"""Synchronous Domains API wrapper.

Provides sync wrappers around the async Domains API.
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
    from collections.abc import Callable

    from oinker.domains._api import AsyncDomainsAPI


class SyncDomainsAPI:
    """Synchronous domain operations for the Porkbun API.

    Accessed via `piglet.domains.*` methods.
    """

    def __init__(
        self,
        async_api: AsyncDomainsAPI,
        runner: Callable[..., Any],
    ) -> None:
        """Initialize sync Domains API."""
        self._async_api = async_api
        self._run = runner

    def list(
        self,
        start: int = 0,
        include_labels: bool = False,
    ) -> builtins.list[DomainInfo]:
        """See :meth:`AsyncDomainsAPI.list`."""
        return self._run(self._async_api.list(start, include_labels))

    def get_nameservers(self, domain: str) -> builtins.list[str]:
        """See :meth:`AsyncDomainsAPI.get_nameservers`."""
        return self._run(self._async_api.get_nameservers(domain))

    def update_nameservers(
        self,
        domain: str,
        nameservers: builtins.list[str],
    ) -> None:
        """See :meth:`AsyncDomainsAPI.update_nameservers`."""
        self._run(self._async_api.update_nameservers(domain, nameservers))

    def get_url_forwards(self, domain: str) -> builtins.list[URLForward]:
        """See :meth:`AsyncDomainsAPI.get_url_forwards`."""
        return self._run(self._async_api.get_url_forwards(domain))

    def add_url_forward(self, domain: str, forward: URLForwardCreate) -> None:
        """See :meth:`AsyncDomainsAPI.add_url_forward`."""
        self._run(self._async_api.add_url_forward(domain, forward))

    def delete_url_forward(self, domain: str, forward_id: str) -> None:
        """See :meth:`AsyncDomainsAPI.delete_url_forward`."""
        self._run(self._async_api.delete_url_forward(domain, forward_id))

    def check(self, domain: str) -> DomainAvailability:
        """See :meth:`AsyncDomainsAPI.check`."""
        return self._run(self._async_api.check(domain))

    def get_glue_records(self, domain: str) -> builtins.list[GlueRecord]:
        """See :meth:`AsyncDomainsAPI.get_glue_records`."""
        return self._run(self._async_api.get_glue_records(domain))

    def create_glue_record(
        self,
        domain: str,
        subdomain: str,
        ips: builtins.list[str],
    ) -> None:
        """See :meth:`AsyncDomainsAPI.create_glue_record`."""
        self._run(self._async_api.create_glue_record(domain, subdomain, ips))

    def update_glue_record(
        self,
        domain: str,
        subdomain: str,
        ips: builtins.list[str],
    ) -> None:
        """See :meth:`AsyncDomainsAPI.update_glue_record`."""
        self._run(self._async_api.update_glue_record(domain, subdomain, ips))

    def delete_glue_record(self, domain: str, subdomain: str) -> None:
        """See :meth:`AsyncDomainsAPI.delete_glue_record`."""
        self._run(self._async_api.delete_glue_record(domain, subdomain))
