"""DNS CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from oinker import OinkerError, Piglet

dns_app = typer.Typer(
    name="dns",
    help="Manage DNS records.",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)


def _get_client(api_key: str | None = None, secret_key: str | None = None) -> Piglet:
    """Create a Piglet client with optional credentials."""
    return Piglet(api_key=api_key, secret_key=secret_key)


@dns_app.command("list")
def list_records(
    domain: Annotated[str, typer.Argument(help="Domain to list records for")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """List all DNS records for a domain.

    Shows a table of all records including ID, name, type, content, and TTL.
    """
    try:
        with _get_client(api_key, secret_key) as client:
            records = client.dns.list(domain)

        if not records:
            console.print(f"\U0001f437 No records found for {domain}")
            return

        table = Table(title=f"\U0001f437 DNS Records for {domain}")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Content", style="white")
        table.add_column("TTL", style="yellow", justify="right")
        table.add_column("Priority", style="magenta", justify="right")

        for record in records:
            # Show priority only if non-zero (MX, SRV, etc.)
            priority_str = str(record.priority) if record.priority else ""
            table.add_row(
                record.id,
                record.name,
                record.record_type,
                record.content,
                str(record.ttl),
                priority_str,
            )

        console.print(table)
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None
