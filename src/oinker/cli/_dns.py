"""DNS CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from oinker import OinkerError, Piglet
from oinker.dns import AAAARecord, ARecord, CNAMERecord, MXRecord, TXTRecord

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


# Record type factory for creating records from CLI args
RECORD_TYPES = {
    "A": ARecord,
    "AAAA": AAAARecord,
    "CNAME": CNAMERecord,
    "MX": MXRecord,
    "TXT": TXTRecord,
}


@dns_app.command("create")
def create_record(
    domain: Annotated[str, typer.Argument(help="Domain to create record for")],
    record_type: Annotated[str, typer.Argument(help="Record type (A, AAAA, CNAME, MX, TXT)")],
    name: Annotated[str, typer.Argument(help="Subdomain name (use @ for root)")],
    content: Annotated[str, typer.Argument(help="Record content (IP, hostname, text)")],
    ttl: Annotated[int, typer.Option("--ttl", "-t", help="Time to live in seconds")] = 600,
    priority: Annotated[
        int | None, typer.Option("--priority", "-p", help="Priority for MX/SRV records")
    ] = None,
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Create a new DNS record.

    Creates a DNS record of the specified type. Use @ for the subdomain name
    to create a record at the root domain.

    Examples:
        oinker dns create example.com A www 1.2.3.4
        oinker dns create example.com MX @ mail.example.com --priority 10
        oinker dns create example.com TXT @ "v=spf1 include:_spf.google.com ~all"
    """
    record_type_upper = record_type.upper()
    if record_type_upper not in RECORD_TYPES:
        supported = ", ".join(RECORD_TYPES.keys())
        err_console.print(
            f"\U0001f437 Oops! Unsupported record type: {record_type}. Supported: {supported}",
            style="bold red",
        )
        raise typer.Exit(code=1)

    # Handle @ for root domain
    subdomain = None if name == "@" else name

    try:
        record_cls = RECORD_TYPES[record_type_upper]
        # MX records need priority
        if record_type_upper == "MX":
            record = record_cls(content=content, name=subdomain, ttl=ttl, priority=priority or 10)
        else:
            record = record_cls(content=content, name=subdomain, ttl=ttl)

        with _get_client(api_key, secret_key) as client:
            record_id = client.dns.create(domain, record)

        console.print(f"\U0001f437 Squeee! Created record {record_id}")
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None


@dns_app.command("delete")
def delete_record(
    domain: Annotated[str, typer.Argument(help="Domain to delete record from")],
    record_id: Annotated[str, typer.Option("--id", "-i", help="Record ID to delete")] = "",
    record_type: Annotated[
        str | None, typer.Option("--type", "-t", help="Record type (for delete by type/name)")
    ] = None,
    name: Annotated[
        str | None, typer.Option("--name", "-n", help="Subdomain name (for delete by type/name)")
    ] = None,
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Delete a DNS record.

    Delete by record ID:
        oinker dns delete example.com --id 123456

    Delete by type and name (deletes ALL matching records):
        oinker dns delete example.com --type A --name www
    """
    if not record_id and not (record_type and name is not None):
        err_console.print(
            "\U0001f437 Oops! Provide --id or both --type and --name",
            style="bold red",
        )
        raise typer.Exit(code=1)

    try:
        with _get_client(api_key, secret_key) as client:
            if record_id:
                client.dns.delete(domain, record_id=record_id)
                console.print(f"\U0001f437 Gobbled up record {record_id}")
            else:
                # Delete by type/name - handle @ for root
                subdomain = "" if name == "@" else (name or "")
                client.dns.delete_by_name_type(domain, record_type, subdomain)  # type: ignore[arg-type]
                console.print(
                    f"\U0001f437 Gobbled up all {record_type} records for "
                    f"{subdomain or 'root'}.{domain}"
                )
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None
