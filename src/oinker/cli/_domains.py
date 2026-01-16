"""Domain CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from oinker import OinkerError
from oinker.cli._utils import console, err_console, get_client

domains_app = typer.Typer(
    name="domains",
    help="Manage domains.",
    no_args_is_help=True,
)


@domains_app.command("list")
def list_domains(
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """List all domains in your account.

    Shows a table of all domains including status, expiration, and settings.
    """
    try:
        with get_client(api_key, secret_key) as client:
            domains = client.domains.list()

        if not domains:
            console.print("\U0001f437 No domains found in your account")
            return

        table = Table(title="\U0001f437 Your Domains")
        table.add_column("Domain", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Expires", style="yellow")
        table.add_column("Auto-Renew", style="magenta")
        table.add_column("WHOIS Privacy", style="blue")

        for domain in domains:
            expires = domain.expire_date.strftime("%Y-%m-%d") if domain.expire_date else "N/A"
            auto_renew = "\u2713" if domain.auto_renew else ""
            whois_privacy = "\u2713" if domain.whois_privacy else ""
            table.add_row(
                domain.domain,
                domain.status,
                expires,
                auto_renew,
                whois_privacy,
            )

        console.print(table)
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None


@domains_app.command("nameservers")
def get_nameservers(
    domain: Annotated[str, typer.Argument(help="Domain to get nameservers for")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Get authoritative nameservers for a domain.

    Shows the nameservers currently configured for the domain.
    """
    try:
        with get_client(api_key, secret_key) as client:
            nameservers = client.domains.get_nameservers(domain)

        if not nameservers:
            console.print(f"\U0001f437 No nameservers found for {domain}")
            return

        console.print(f"\U0001f437 Nameservers for [cyan]{domain}[/cyan]:")
        for ns in nameservers:
            console.print(f"   {ns}")
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None
