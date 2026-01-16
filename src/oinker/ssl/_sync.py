"""Synchronous SSL API wrapper.

Provides sync wrappers around the async SSL API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oinker.ssl._types import SSLBundle

if TYPE_CHECKING:
    from collections.abc import Callable

    from oinker.ssl._api import AsyncSSLAPI


class SyncSSLAPI:
    """Synchronous SSL operations for the Porkbun API.

    Accessed via `piglet.ssl.*` methods.
    """

    def __init__(
        self,
        async_api: AsyncSSLAPI,
        runner: Callable[..., Any],
    ) -> None:
        """Initialize sync SSL API."""
        self._async_api = async_api
        self._run = runner

    def retrieve(self, domain: str) -> SSLBundle:
        """See :meth:`AsyncSSLAPI.retrieve`."""
        return self._run(self._async_api.retrieve(domain))
