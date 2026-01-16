"""Shared CLI utilities."""

from __future__ import annotations

from rich.console import Console

from oinker import Piglet

console = Console()
err_console = Console(stderr=True)


def get_client(api_key: str | None = None, secret_key: str | None = None) -> Piglet:
    """Create a Piglet client with optional credentials.

    Args:
        api_key: Porkbun API key. Falls back to PORKBUN_API_KEY env var.
        secret_key: Porkbun secret key. Falls back to PORKBUN_SECRET_KEY env var.

    Returns:
        Configured Piglet client.
    """
    return Piglet(api_key=api_key, secret_key=secret_key)
