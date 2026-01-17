"""Shared CLI utilities."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import typer
from rich.console import Console

from oinker import OinkerError, Piglet

if TYPE_CHECKING:
    from collections.abc import Iterator

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


@contextmanager
def handle_errors() -> Iterator[None]:
    """Context manager that handles OinkerError exceptions for CLI commands.

    Catches OinkerError and prints a user-friendly message before exiting.

    Usage:
        with handle_errors():
            with get_client(api_key, secret_key) as client:
                result = client.dns.list(domain)
    """
    try:
        yield
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from e
