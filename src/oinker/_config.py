"""Configuration and authentication handling for oinker.

Credentials can be provided via:
1. Constructor arguments (highest priority)
2. Environment variables PORKBUN_API_KEY and PORKBUN_SECRET_KEY
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Final

# Environment variable names
ENV_API_KEY: Final[str] = "PORKBUN_API_KEY"
ENV_SECRET_KEY: Final[str] = "PORKBUN_SECRET_KEY"

# Porkbun API base URL
BASE_URL: Final[str] = "https://api.porkbun.com/api/json/v3"

# Default configuration values
DEFAULT_TIMEOUT: Final[float] = 30.0
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_RETRY_DELAY: Final[float] = 1.0


@dataclass(frozen=True, slots=True)
class OinkerConfig:
    """Configuration for the oinker client.

    Attributes:
        api_key: Porkbun API key (pk1_...).
        secret_key: Porkbun secret key (sk1_...).
        base_url: API base URL (rarely needs changing).
        timeout: Request timeout in seconds.
        max_retries: Maximum retry attempts for transient failures.
        retry_delay: Initial delay between retries in seconds.
    """

    api_key: str = field(default="")
    secret_key: str = field(default="")
    base_url: str = field(default=BASE_URL)
    timeout: float = field(default=DEFAULT_TIMEOUT)
    max_retries: int = field(default=DEFAULT_MAX_RETRIES)
    retry_delay: float = field(default=DEFAULT_RETRY_DELAY)

    def __post_init__(self) -> None:
        """Resolve credentials from environment if not provided."""
        # Use object.__setattr__ since this is a frozen dataclass
        if not self.api_key:
            object.__setattr__(self, "api_key", os.environ.get(ENV_API_KEY, ""))
        if not self.secret_key:
            object.__setattr__(self, "secret_key", os.environ.get(ENV_SECRET_KEY, ""))

    @property
    def has_credentials(self) -> bool:
        """Check if both API key and secret key are configured."""
        return bool(self.api_key and self.secret_key)

    @property
    def auth_body(self) -> dict[str, str]:
        """Return the authentication body for API requests."""
        return {
            "apikey": self.api_key,
            "secretapikey": self.secret_key,
        }
