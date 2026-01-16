"""Main CLI entry point using Typer."""

from __future__ import annotations

from typing import Annotated

import typer

from oinker import OinkerError
from oinker.cli._dns import dns_app
from oinker.cli._dnssec import dnssec_app
from oinker.cli._domains import domains_app
from oinker.cli._pricing import pricing_app
from oinker.cli._ssl import ssl_app
from oinker.cli._utils import console, err_console, get_client

app = typer.Typer(
    name="oinker",
    help="\U0001f437 Oinker - Porkbun DNS management that doesn't stink!",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(dns_app, name="dns")
app.add_typer(dnssec_app, name="dnssec")
app.add_typer(domains_app, name="domains")
app.add_typer(pricing_app, name="pricing")
app.add_typer(ssl_app, name="ssl")


@app.command()
def ping(
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Test API connectivity and authentication.

    Verifies your credentials work and shows your public IP address.
    """
    try:
        with get_client(api_key, secret_key) as client:
            response = client.ping()
        console.print("\U0001f437 Oink! Connected successfully.")
        console.print(f"   Your IP: {response.your_ip}")
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None


if __name__ == "__main__":
    app()
