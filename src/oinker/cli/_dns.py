"""DNS CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from oinker.cli._utils import console, err_console, get_client, handle_errors
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
    with handle_errors():
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

    with handle_errors():
        record_cls = RECORD_TYPES[record_type_upper]
        # MX records need priority
        if record_type_upper == "MX":
            record = record_cls(content=content, name=subdomain, ttl=ttl, priority=priority or 10)
        else:
            record = record_cls(content=content, name=subdomain, ttl=ttl)

        with get_client(api_key, secret_key) as client:
            record_id = client.dns.create(domain, record)

        console.print(f"\U0001f437 Squeee! Created record {record_id}")


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

    with handle_errors(), get_client(api_key, secret_key) as client:
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

    with handle_errors():
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


def _resolve_subdomain(
    name: str | None, domain: str, existing_name: str | None = None
) -> str | None:
    """Resolve subdomain from CLI input.

    Args:
        name: CLI --name argument (@ means root, None means use existing).
        domain: The base domain.
        existing_name: Existing record's full name for fallback extraction.

    Returns:
        Subdomain string or None for root.
    """
    if name == "@":
        return None
    if name is not None:
        return name
    if existing_name is None:
        return None

    # Extract subdomain from existing record's full name
    subdomain = existing_name.removesuffix(f".{domain}") or None
    return None if subdomain == domain else subdomain


def _build_updated_record(
    record_type: str,
    content: str,
    subdomain: str | None,
    ttl: int,
    priority: int | None,
    notes: str | None,
) -> ARecord | AAAARecord | CNAMERecord | MXRecord | TXTRecord:
    """Build a DNS record instance for editing.

    Args:
        record_type: Record type (A, AAAA, CNAME, MX, TXT).
        content: Record content value.
        subdomain: Subdomain name or None for root.
        ttl: TTL in seconds.
        priority: Priority for MX records.
        notes: Optional notes to attach.

    Returns:
        Constructed DNS record instance.
    """
    record_cls = RECORD_TYPES[record_type]

    if record_type == "MX":
        record = record_cls(content=content, name=subdomain, ttl=ttl, priority=priority or 10)
    else:
        record = record_cls(content=content, name=subdomain, ttl=ttl)

    if notes is not None:
        object.__setattr__(record, "notes", notes)

    return record


def _edit_record_by_id(
    domain: str,
    record_id: str,
    content: str,
    name: str | None,
    ttl: int | None,
    priority: int | None,
    notes: str | None,
    api_key: str | None,
    secret_key: str | None,
) -> None:
    """Edit a DNS record by its ID.

    Args:
        domain: Domain the record belongs to.
        record_id: ID of the record to edit.
        content: New content value.
        name: New subdomain name (@ for root, None to keep existing).
        ttl: New TTL or None to keep existing.
        priority: New priority or None to keep existing.
        notes: New notes or None to keep existing.
        api_key: Porkbun API key.
        secret_key: Porkbun secret key.
    """
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

        subdomain = _resolve_subdomain(name, domain, existing.name)
        new_ttl = ttl if ttl is not None else existing.ttl
        new_priority = priority if priority is not None else existing.priority

        new_record = _build_updated_record(
            record_type_upper, content, subdomain, new_ttl, new_priority, notes
        )
        client.dns.edit(domain, record_id, new_record)

    console.print(f"\U0001f437 Updated record {record_id}")


def _edit_record_by_type_name(
    domain: str,
    record_type: str,
    name: str | None,
    content: str,
    ttl: int | None,
    priority: int | None,
    notes: str | None,
    api_key: str | None,
    secret_key: str | None,
) -> None:
    """Edit DNS records by type and name.

    Args:
        domain: Domain the records belong to.
        record_type: Record type to match.
        name: Subdomain name to match (@ for root).
        content: New content value.
        ttl: New TTL or None to keep existing.
        priority: New priority or None to keep existing.
        notes: New notes or None to keep existing.
        api_key: Porkbun API key.
        secret_key: Porkbun secret key.
    """
    subdomain = None if name == "@" else name
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

    if not content:
        err_console.print(
            "\U0001f437 Oops! --content is required",
            style="bold red",
        )
        raise typer.Exit(code=1)

    with handle_errors():
        if record_id:
            _edit_record_by_id(
                domain, record_id, content, name, ttl, priority, notes, api_key, secret_key
            )
        else:
            assert record_type is not None
            _edit_record_by_type_name(
                domain, record_type, name, content, ttl, priority, notes, api_key, secret_key
            )
