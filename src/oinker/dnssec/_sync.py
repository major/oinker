"""Synchronous DNSSEC API wrapper.

Provides sync wrappers around the async DNSSEC API.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from oinker._sync_base import SyncAPIBase
from oinker.dnssec._types import DNSSECRecord, DNSSECRecordCreate

if TYPE_CHECKING:
    from oinker.dnssec._api import AsyncDNSSECAPI  # noqa: F401


class SyncDNSSECAPI(SyncAPIBase["AsyncDNSSECAPI"]):
    """Synchronous DNSSEC operations for the Porkbun API.

    Accessed via `piglet.dnssec.*` methods.
    """

    def list(self, domain: str) -> builtins.list[DNSSECRecord]:
        """See :meth:`AsyncDNSSECAPI.list`."""
        return self._run(self._async_api.list(domain))

    def create(self, domain: str, record: DNSSECRecordCreate) -> None:
        """See :meth:`AsyncDNSSECAPI.create`."""
        self._run(self._async_api.create(domain, record))

    def delete(self, domain: str, key_tag: str) -> None:
        """See :meth:`AsyncDNSSECAPI.delete`."""
        self._run(self._async_api.delete(domain, key_tag))
