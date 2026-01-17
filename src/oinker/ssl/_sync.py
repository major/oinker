"""Synchronous SSL API wrapper.

Provides sync wrappers around the async SSL API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from oinker._sync_base import SyncAPIBase
from oinker.ssl._types import SSLBundle

if TYPE_CHECKING:
    from oinker.ssl._api import AsyncSSLAPI  # noqa: F401


class SyncSSLAPI(SyncAPIBase["AsyncSSLAPI"]):
    """Synchronous SSL operations for the Porkbun API.

    Accessed via `piglet.ssl.*` methods.
    """

    def retrieve(self, domain: str) -> SSLBundle:
        """See :meth:`AsyncSSLAPI.retrieve`."""
        return self._run(self._async_api.retrieve(domain))
