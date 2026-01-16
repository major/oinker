"""Synchronous DNSSEC API wrapper.

Provides sync wrappers around the async DNSSEC API.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from oinker.dnssec._types import DNSSECRecord, DNSSECRecordCreate

if TYPE_CHECKING:
    from collections.abc import Callable

    from oinker.dnssec._api import AsyncDNSSECAPI


class SyncDNSSECAPI:
    """Synchronous DNSSEC operations for the Porkbun API.

    Accessed via `piglet.dnssec.*` methods.
    """

    def __init__(
        self,
        async_api: AsyncDNSSECAPI,
        runner: Callable[..., Any],
    ) -> None:
        """Initialize sync DNSSEC API."""
        self._async_api = async_api
        self._run = runner

    def list(self, domain: str) -> builtins.list[DNSSECRecord]:
        """See :meth:`AsyncDNSSECAPI.list`."""
        return self._run(self._async_api.list(domain))

    def create(self, domain: str, record: DNSSECRecordCreate) -> None:
        """See :meth:`AsyncDNSSECAPI.create`."""
        self._run(self._async_api.create(domain, record))

    def delete(self, domain: str, key_tag: str) -> None:
        """See :meth:`AsyncDNSSECAPI.delete`."""
        self._run(self._async_api.delete(domain, key_tag))
