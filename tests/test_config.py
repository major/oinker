"""Tests for oinker configuration handling."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from oinker._config import ENV_API_KEY, ENV_SECRET_KEY, OinkerConfig


class TestOinkerConfig:
    """Tests for OinkerConfig."""

    def test_explicit_credentials(self) -> None:
        """Config should use explicitly provided credentials."""
        config = OinkerConfig(api_key="pk1_test", secret_key="sk1_test")
        assert config.api_key == "pk1_test"
        assert config.secret_key == "sk1_test"

    def test_env_var_fallback(self) -> None:
        """Config should fall back to environment variables."""
        with patch.dict(
            os.environ,
            {ENV_API_KEY: "pk1_from_env", ENV_SECRET_KEY: "sk1_from_env"},
        ):
            config = OinkerConfig()
            assert config.api_key == "pk1_from_env"
            assert config.secret_key == "sk1_from_env"

    def test_explicit_overrides_env(self) -> None:
        """Explicit credentials should override environment variables."""
        with patch.dict(
            os.environ,
            {ENV_API_KEY: "pk1_from_env", ENV_SECRET_KEY: "sk1_from_env"},
        ):
            config = OinkerConfig(api_key="pk1_explicit", secret_key="sk1_explicit")
            assert config.api_key == "pk1_explicit"
            assert config.secret_key == "sk1_explicit"

    def test_missing_credentials(self) -> None:
        """Config should handle missing credentials gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the env vars if they exist
            os.environ.pop(ENV_API_KEY, None)
            os.environ.pop(ENV_SECRET_KEY, None)
            config = OinkerConfig()
            assert config.api_key == ""
            assert config.secret_key == ""

    def test_has_credentials_true(self) -> None:
        """has_credentials should be True when both keys are set."""
        config = OinkerConfig(api_key="pk1_test", secret_key="sk1_test")
        assert config.has_credentials is True

    def test_has_credentials_false_missing_api_key(self) -> None:
        """has_credentials should be False when api_key is missing."""
        config = OinkerConfig(api_key="", secret_key="sk1_test")
        assert config.has_credentials is False

    def test_has_credentials_false_missing_secret_key(self) -> None:
        """has_credentials should be False when secret_key is missing."""
        config = OinkerConfig(api_key="pk1_test", secret_key="")
        assert config.has_credentials is False

    def test_auth_body(self) -> None:
        """auth_body should return correct format for API requests."""
        config = OinkerConfig(api_key="pk1_test", secret_key="sk1_test")
        assert config.auth_body == {
            "apikey": "pk1_test",
            "secretapikey": "sk1_test",
        }

    def test_default_values(self) -> None:
        """Config should have sensible defaults."""
        config = OinkerConfig(api_key="pk1_test", secret_key="sk1_test")
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert "porkbun.com" in config.base_url

    def test_custom_values(self) -> None:
        """Config should accept custom values."""
        config = OinkerConfig(
            api_key="pk1_test",
            secret_key="sk1_test",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            base_url="https://custom.api.example.com",
        )
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.base_url == "https://custom.api.example.com"

    def test_frozen_dataclass(self) -> None:
        """Config should be immutable after creation."""
        config = OinkerConfig(api_key="pk1_test", secret_key="sk1_test")
        with pytest.raises(AttributeError):
            config.api_key = "different_key"  # type: ignore[misc]
