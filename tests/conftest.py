"""Shared pytest fixtures for oinker tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from oinker import Piglet
from oinker._config import OinkerConfig
from oinker._http import HttpClient


def make_response(data: dict[str, Any], status_code: int = 200) -> httpx.Response:
    """Create a mock httpx.Response for testing.

    Args:
        data: JSON data for the response body.
        status_code: HTTP status code (default: 200).

    Returns:
        A mock httpx.Response with the given data and status code.
    """
    return httpx.Response(status_code, json=data)


@pytest.fixture
def api_credentials() -> dict[str, str]:
    """Test API credentials."""
    return {"api_key": "pk1_test_key", "secret_key": "sk1_test_secret"}


@pytest.fixture
def config(api_credentials: dict[str, str]) -> OinkerConfig:
    """Test configuration with credentials."""
    return OinkerConfig(
        api_key=api_credentials["api_key"],
        secret_key=api_credentials["secret_key"],
    )


@pytest.fixture
def config_no_retry(api_credentials: dict[str, str]) -> OinkerConfig:
    """Test configuration with no retries for fast unit tests."""
    return OinkerConfig(
        api_key=api_credentials["api_key"],
        secret_key=api_credentials["secret_key"],
        max_retries=0,
        retry_delay=0.01,
    )


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx.AsyncClient for testing."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def http_client(config: OinkerConfig, mock_httpx_client: AsyncMock) -> HttpClient:
    """HttpClient with mocked transport."""
    return HttpClient(config, client=mock_httpx_client)


@pytest.fixture
def success_response() -> dict[str, Any]:
    """Successful API response."""
    return {"status": "SUCCESS", "yourIp": "203.0.113.42"}


@pytest.fixture
def error_response() -> dict[str, str]:
    """Error API response."""
    return {"status": "ERROR", "message": "Something went wrong"}


@pytest.fixture
def mock_piglet_client() -> MagicMock:
    """Mock Piglet client with context manager support for CLI tests."""
    mock = MagicMock(spec=Piglet)
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    return mock
