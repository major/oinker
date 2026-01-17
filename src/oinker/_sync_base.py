"""Base class for sync API wrappers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class SyncAPIBase[AsyncAPIType]:
    """Base class for synchronous API wrappers.

    Provides common initialization for all sync API wrappers that delegate
    to their async counterparts.
    """

    def __init__(
        self,
        async_api: AsyncAPIType,
        runner: Callable[..., Any],
    ) -> None:
        self._async_api = async_api
        self._run = runner
