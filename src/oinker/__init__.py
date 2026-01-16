"""Oinker - A delightfully Pythonic library for managing DNS at Porkbun.

from oinker import Piglet, AsyncPiglet

# Async (recommended for performance)
async with AsyncPiglet() as piglet:
    pong = await piglet.ping()
    print(f"Your IP: {pong.your_ip}")

# Sync (for scripts and simple use)
with Piglet() as piglet:
    pong = piglet.ping()
"""

from oinker._client import AsyncPiglet
from oinker._exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    OinkerError,
    RateLimitError,
    ValidationError,
)
from oinker._sync import Piglet
from oinker._types import PingResponse

__all__ = [
    # Clients
    "AsyncPiglet",
    "Piglet",
    # Types
    "PingResponse",
    # Exceptions
    "OinkerError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "APIError",
]

__version__ = "0.1.0"
