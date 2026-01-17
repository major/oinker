"""DNSSEC CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from oinker.cli._utils import console, get_client, handle_errors
from oinker.dnssec import DNSSECRecordCreate

dnssec_app = typer.Typer(
    name="dnssec",
    help="Manage DNSSEC records at the registry.",
    no_args_is_help=True,
)


@dnssec_app.command("list")
def list_dnssec_records(
    domain: Annotated[str, typer.Argument(help="Domain to list DNSSEC records for")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """List DNSSEC records for a domain.

    Shows DS records registered at the domain registry.
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            records = client.dnssec.list(domain)

        if not records:
            console.print(f"\U0001f437 No DNSSEC records found for {domain}")
            return

        table = Table(title=f"\U0001f437 DNSSEC Records for {domain}")
        table.add_column("Key Tag", style="cyan")
        table.add_column("Algorithm", style="green")
        table.add_column("Digest Type", style="yellow")
        table.add_column("Digest", style="white", max_width=40)

        for record in records:
            digest_display = (
                record.digest[:37] + "..." if len(record.digest) > 40 else record.digest
            )
            table.add_row(
                record.key_tag,
                record.algorithm,
                record.digest_type,
                digest_display,
            )

        console.print(table)


@dnssec_app.command("create")
def create_dnssec_record(
    domain: Annotated[str, typer.Argument(help="Domain to create DNSSEC record for")],
    key_tag: Annotated[str, typer.Argument(help="Key tag (e.g., 64087)")],
    algorithm: Annotated[str, typer.Argument(help="DS algorithm (e.g., 13)")],
    digest_type: Annotated[str, typer.Argument(help="Digest type (e.g., 2)")],
    digest: Annotated[str, typer.Argument(help="Digest value (hex string)")],
    max_sig_life: Annotated[
        str | None, typer.Option("--max-sig-life", help="Max signature life")
    ] = None,
    key_data_flags: Annotated[
        str | None, typer.Option("--key-data-flags", help="Key data flags")
    ] = None,
    key_data_protocol: Annotated[
        str | None, typer.Option("--key-data-protocol", help="Key data protocol")
    ] = None,
    key_data_algorithm: Annotated[
        str | None, typer.Option("--key-data-algorithm", help="Key data algorithm")
    ] = None,
    key_data_public_key: Annotated[
        str | None, typer.Option("--key-data-public-key", help="Key data public key")
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
    """Create a DNSSEC record at the registry.

    Most registries only require the DS data fields (key_tag, algorithm,
    digest_type, digest). The key data options are rarely needed.

    Examples:
        oinker dnssec create example.com 64087 13 2 15E445BD08128BDC...
    """
    with handle_errors():
        record = DNSSECRecordCreate(
            key_tag=key_tag,
            algorithm=algorithm,
            digest_type=digest_type,
            digest=digest,
            max_sig_life=max_sig_life,
            key_data_flags=key_data_flags,
            key_data_protocol=key_data_protocol,
            key_data_algorithm=key_data_algorithm,
            key_data_public_key=key_data_public_key,
        )
        with get_client(api_key, secret_key) as client:
            client.dnssec.create(domain, record)

        console.print(f"\U0001f437 Created DNSSEC record with key tag {key_tag}")


@dnssec_app.command("delete")
def delete_dnssec_record(
    domain: Annotated[str, typer.Argument(help="Domain to delete DNSSEC record from")],
    key_tag: Annotated[str, typer.Argument(help="Key tag of record to delete")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Delete a DNSSEC record from the registry.

    Note: Most registries delete all records with matching data, not just
    the record with the matching key tag.

    Examples:
        oinker dnssec delete example.com 64087
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            client.dnssec.delete(domain, key_tag)

        console.print(f"\U0001f437 Deleted DNSSEC record with key tag {key_tag}")
