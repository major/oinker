"""DNS CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from oinker import OinkerError
from oinker.cli._utils import console, err_console, get_client
from oinker.dns import AAAARecord, ARecord, CNAMERecord, MXRecord, TXTRecord

dns_app = typer.Typer(
    name="dns",
    help="Manage DNS records.",
    no_args_is_help=True,
)


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
        with get_client(api_key, secret_key) as client:
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

        with get_client(api_key, secret_key) as client:
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
        with get_client(api_key, secret_key) as client:
            if record_id:
                client.dns.delete(domain, record_id=record_id)
                console.print(f"\U0001f437 Gobbled up record {record_id}")
            else:
                # Delete by type/name - handle @ for root
                subdomain = "" if name == "@" else (name or "")
                assert record_type is not None  # Validated at line 166
                client.dns.delete_by_name_type(domain, record_type, subdomain)
                console.print(
                    f"\U0001f437 Gobbled up all {record_type} records for "
                    f"{subdomain or 'root'}.{domain}"
                )
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None


@dns_app.command("get")
def get_record(
    domain: Annotated[str, typer.Argument(help="Domain to get record from")],
    record_id: Annotated[str | None, typer.Option("--id", "-i", help="Record ID")] = None,
    record_type: Annotated[
        str | None, typer.Option("--type", "-t", help="Record type (for get by type/name)")
    ] = None,
    name: Annotated[
        str | None, typer.Option("--name", "-n", help="Subdomain name (use @ for root)")
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
    """Get a specific DNS record.

    Get by record ID:
        oinker dns get example.com --id 123456

    Get by type and name:
        oinker dns get example.com --type A --name www
    """
    if not record_id and not record_type:
        err_console.print(
            "\U0001f437 Oops! Provide --id or --type",
            style="bold red",
        )
        raise typer.Exit(code=1)

    try:
        with get_client(api_key, secret_key) as client:
            if record_id:
                record = client.dns.get(domain, record_id)
                records = [record] if record else []
            else:
                subdomain = None if name == "@" else name
                assert record_type is not None
                records = client.dns.get_by_name_type(domain, record_type.upper(), subdomain)

        if not records:
            console.print("\U0001f437 No matching records found")
            return

        table = Table(title="\U0001f437 DNS Record(s)")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Content", style="white")
        table.add_column("TTL", style="yellow", justify="right")
        table.add_column("Priority", style="magenta", justify="right")
        table.add_column("Notes", style="dim")

        for record in records:
            priority_str = str(record.priority) if record.priority else ""
            table.add_row(
                record.id,
                record.name,
                record.record_type,
                record.content,
                str(record.ttl),
                priority_str,
                record.notes or "",
            )

        console.print(table)
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None


@dns_app.command("edit")
def edit_record(
    domain: Annotated[str, typer.Argument(help="Domain to edit record for")],
    record_id: Annotated[str | None, typer.Option("--id", "-i", help="Record ID to edit")] = None,
    record_type: Annotated[
        str | None, typer.Option("--type", "-t", help="Record type (for edit by type/name)")
    ] = None,
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Subdomain name for type/name edit (use @ for root)"),
    ] = None,
    content: Annotated[
        str | None, typer.Option("--content", "-c", help="New content value")
    ] = None,
    ttl: Annotated[int | None, typer.Option("--ttl", help="New TTL in seconds")] = None,
    priority: Annotated[
        int | None, typer.Option("--priority", "-p", help="New priority for MX/SRV records")
    ] = None,
    notes: Annotated[
        str | None, typer.Option("--notes", help="Notes (empty string clears)")
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
    """Edit a DNS record.

    Edit by ID (requires full record data):
        oinker dns edit example.com --id 123456 --content 1.2.3.5

    Edit by type/name (updates all matching records):
        oinker dns edit example.com --type A --name www --content 1.2.3.5
    """
    if not record_id and not record_type:
        err_console.print(
            "\U0001f437 Oops! Provide --id or --type",
            style="bold red",
        )
        raise typer.Exit(code=1)

    if record_id:
        if not content:
            err_console.print(
                "\U0001f437 Oops! --content is required when editing by ID",
                style="bold red",
            )
            raise typer.Exit(code=1)

        try:
            with get_client(api_key, secret_key) as client:
                existing = client.dns.get(domain, record_id)
                if not existing:
                    err_console.print(
                        f"\U0001f437 Oops! Record {record_id} not found",
                        style="bold red",
                    )
                    raise typer.Exit(code=1)

                record_type_upper = existing.record_type.upper()
                if record_type_upper not in RECORD_TYPES:
                    err_console.print(
                        f"\U0001f437 Oops! Editing {record_type_upper} not supported via CLI",
                        style="bold red",
                    )
                    raise typer.Exit(code=1)

                record_cls = RECORD_TYPES[record_type_upper]
                existing_subdomain = existing.name.removesuffix(f".{domain}") or None
                if existing_subdomain == domain:
                    existing_subdomain = None
                subdomain = None if name == "@" else (name if name else existing_subdomain)

                new_ttl = ttl if ttl is not None else existing.ttl
                if record_type_upper == "MX":
                    new_priority = priority if priority is not None else existing.priority or 10
                    new_record = record_cls(
                        content=content, name=subdomain, ttl=new_ttl, priority=new_priority
                    )
                else:
                    new_record = record_cls(content=content, name=subdomain, ttl=new_ttl)

                if notes is not None:
                    object.__setattr__(new_record, "notes", notes)

                client.dns.edit(domain, record_id, new_record)

            console.print(f"\U0001f437 Updated record {record_id}")
        except OinkerError as e:
            err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
            raise typer.Exit(code=1) from None
    else:
        if not content:
            err_console.print(
                "\U0001f437 Oops! --content is required when editing by type/name",
                style="bold red",
            )
            raise typer.Exit(code=1)

        try:
            subdomain = None if name == "@" else name
            assert record_type is not None
            with get_client(api_key, secret_key) as client:
                client.dns.edit_by_name_type(
                    domain,
                    record_type.upper(),
                    subdomain,
                    content=content,
                    ttl=ttl,
                    priority=priority,
                    notes=notes,
                )

            name_display = name or "root"
            console.print(
                f"\U0001f437 Updated all {record_type.upper()} records for {name_display}.{domain}"
            )
        except OinkerError as e:
            err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
            raise typer.Exit(code=1) from None
