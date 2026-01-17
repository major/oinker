"""SSL CLI subcommands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from oinker import OinkerError
from oinker.cli._utils import console, err_console, get_client

ssl_app = typer.Typer(
    name="ssl",
    help="Retrieve SSL certificates.",
    no_args_is_help=True,
)


@ssl_app.command("retrieve")
def retrieve_ssl(
    domain: Annotated[str, typer.Argument(help="Domain to retrieve SSL certificate for")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Directory to save certificate files (creates domain.crt, domain.key, domain.pub)",
        ),
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
    """Retrieve SSL certificate bundle for a domain.

    By default, displays the certificate chain. Use --output to save
    certificate files to a directory.

    Examples:
        oinker ssl retrieve example.com
        oinker ssl retrieve example.com --output /etc/ssl/certs/
    """
    try:
        with get_client(api_key, secret_key) as client:
            bundle = client.ssl.retrieve(domain)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

            cert_file = output_dir / f"{domain}.crt"
            key_file = output_dir / f"{domain}.key"
            pub_file = output_dir / f"{domain}.pub"

            cert_file.write_text(bundle.certificate_chain)
            key_file.write_text(bundle.private_key)
            key_file.chmod(0o600)
            pub_file.write_text(bundle.public_key)

            console.print(f"\U0001f437 SSL certificate files saved to {output_dir}/")
            console.print(f"   Certificate chain: {cert_file}")
            console.print(f"   Private key: {key_file} [dim](mode 600)[/dim]")
            console.print(f"   Public key: {pub_file}")
        else:
            console.print(f"\U0001f437 SSL Certificate for [cyan]{domain}[/cyan]\n")
            console.print("[bold]Certificate Chain:[/bold]")
            console.print(bundle.certificate_chain)
            console.print("\n[bold]Public Key:[/bold]")
            console.print(bundle.public_key)
            console.print("\n[dim]Use --output to save files including private key[/dim]")
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None
