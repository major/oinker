"""Domain CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from oinker.cli._utils import console, err_console, get_client, handle_errors
from oinker.domains import URLForwardCreate

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
    with handle_errors():
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
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            nameservers = client.domains.get_nameservers(domain)

        if not nameservers:
            console.print(f"\U0001f437 No nameservers found for {domain}")
            return

        console.print(f"\U0001f437 Nameservers for [cyan]{domain}[/cyan]:")
        for ns in nameservers:
            console.print(f"   {ns}")


@domains_app.command("update-nameservers")
def update_nameservers(
    domain: Annotated[str, typer.Argument(help="Domain to update nameservers for")],
    nameservers: Annotated[
        list[str],
        typer.Argument(help="Nameserver hostnames (e.g., ns1.example.com ns2.example.com)"),
    ],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Update the nameservers for a domain.

    Examples:
        oinker domains update-nameservers example.com ns1.example.com ns2.example.com
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            client.domains.update_nameservers(domain, nameservers)

        console.print(f"\U0001f437 Updated nameservers for [cyan]{domain}[/cyan]:")
        for ns in nameservers:
            console.print(f"   {ns}")


@domains_app.command("check")
def check_availability(
    domain: Annotated[str, typer.Argument(help="Domain to check availability for")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Check if a domain is available for registration.

    Note: Domain checks are rate limited.

    Examples:
        oinker domains check example.com
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            result = client.domains.check(domain)

        if result.available:
            console.print(f"\U0001f437 [green]{domain}[/green] is available!")
        else:
            console.print(f"\U0001f437 [red]{domain}[/red] is not available")

        table = Table(title="Pricing")
        table.add_column("Type", style="cyan")
        table.add_column("Price", style="green", justify="right")
        table.add_column("Regular Price", style="yellow", justify="right")

        table.add_row("Registration", f"${result.price}", f"${result.regular_price}")
        if result.renewal:
            table.add_row("Renewal", f"${result.renewal.price}", f"${result.renewal.regular_price}")
        if result.transfer:
            table.add_row(
                "Transfer", f"${result.transfer.price}", f"${result.transfer.regular_price}"
            )

        console.print(table)

        if result.first_year_promo:
            console.print("   [yellow]First year promo pricing available![/yellow]")
        if result.premium:
            console.print("   [magenta]This is a premium domain[/magenta]")


@domains_app.command("forwards-list")
def list_url_forwards(
    domain: Annotated[str, typer.Argument(help="Domain to list URL forwards for")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """List URL forwarding rules for a domain."""
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            forwards = client.domains.get_url_forwards(domain)

        if not forwards:
            console.print(f"\U0001f437 No URL forwards found for {domain}")
            return

        table = Table(title=f"\U0001f437 URL Forwards for {domain}")
        table.add_column("ID", style="dim")
        table.add_column("Subdomain", style="cyan")
        table.add_column("Location", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Include Path", style="magenta")
        table.add_column("Wildcard", style="blue")

        for forward in forwards:
            subdomain = forward.subdomain or "(root)"
            include_path = "\u2713" if forward.include_path else ""
            wildcard = "\u2713" if forward.wildcard else ""
            table.add_row(
                forward.id,
                subdomain,
                forward.location,
                forward.type,
                include_path,
                wildcard,
            )

        console.print(table)


@domains_app.command("forwards-add")
def add_url_forward(
    domain: Annotated[str, typer.Argument(help="Domain to add URL forward for")],
    location: Annotated[str, typer.Argument(help="Destination URL")],
    subdomain: Annotated[
        str | None, typer.Option("--subdomain", "-n", help="Subdomain to forward (omit for root)")
    ] = None,
    forward_type: Annotated[
        str, typer.Option("--type", "-t", help="Redirect type: temporary or permanent")
    ] = "temporary",
    include_path: Annotated[
        bool, typer.Option("--include-path", "-p", help="Include URI path in redirect")
    ] = False,
    wildcard: Annotated[
        bool, typer.Option("--wildcard", "-w", help="Forward all subdomains")
    ] = False,
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Add a URL forwarding rule.

    Examples:
        oinker domains forwards-add example.com https://newsite.com
        oinker domains forwards-add example.com https://blog.com --subdomain blog
        oinker domains forwards-add example.com https://newsite.com --type permanent --wildcard
    """
    if forward_type not in ("temporary", "permanent"):
        err_console.print(
            "\U0001f437 Oops! --type must be 'temporary' or 'permanent'",
            style="bold red",
        )
        raise typer.Exit(code=1)

    with handle_errors():
        forward = URLForwardCreate(
            location=location,
            type=forward_type,  # type: ignore[arg-type]
            subdomain=subdomain,
            include_path=include_path,
            wildcard=wildcard,
        )
        with get_client(api_key, secret_key) as client:
            client.domains.add_url_forward(domain, forward)

        subdomain_display = subdomain or "(root)"
        console.print(
            f"\U0001f437 Added URL forward: [cyan]{subdomain_display}.{domain}[/cyan] -> {location}"
        )


@domains_app.command("forwards-delete")
def delete_url_forward(
    domain: Annotated[str, typer.Argument(help="Domain to delete URL forward from")],
    forward_id: Annotated[str, typer.Argument(help="Forward ID to delete")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Delete a URL forwarding rule.

    Examples:
        oinker domains forwards-delete example.com 12345678
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            client.domains.delete_url_forward(domain, forward_id)

        console.print(f"\U0001f437 Deleted URL forward {forward_id}")


@domains_app.command("glue-list")
def list_glue_records(
    domain: Annotated[str, typer.Argument(help="Domain to list glue records for")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """List glue records for a domain."""
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            records = client.domains.get_glue_records(domain)

        if not records:
            console.print(f"\U0001f437 No glue records found for {domain}")
            return

        table = Table(title=f"\U0001f437 Glue Records for {domain}")
        table.add_column("Hostname", style="cyan")
        table.add_column("IPv4", style="green")
        table.add_column("IPv6", style="yellow")

        for record in records:
            ipv4 = ", ".join(record.ipv4) or "-"
            ipv6 = ", ".join(record.ipv6) or "-"
            table.add_row(record.hostname, ipv4, ipv6)

        console.print(table)


@domains_app.command("glue-create")
def create_glue_record(
    domain: Annotated[str, typer.Argument(help="Domain to create glue record for")],
    subdomain: Annotated[str, typer.Argument(help="Glue host subdomain (e.g., ns1)")],
    ips: Annotated[list[str], typer.Argument(help="IP addresses (IPv4 and/or IPv6)")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Create a glue record.

    Examples:
        oinker domains glue-create example.com ns1 192.168.1.1
        oinker domains glue-create example.com ns1 192.168.1.1 2001:db8::1
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            client.domains.create_glue_record(domain, subdomain, ips)

        console.print(f"\U0001f437 Created glue record [cyan]{subdomain}.{domain}[/cyan]")


@domains_app.command("glue-update")
def update_glue_record(
    domain: Annotated[str, typer.Argument(help="Domain to update glue record for")],
    subdomain: Annotated[str, typer.Argument(help="Glue host subdomain (e.g., ns1)")],
    ips: Annotated[list[str], typer.Argument(help="New IP addresses (replaces existing)")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Update a glue record (replaces all IPs).

    Examples:
        oinker domains glue-update example.com ns1 192.168.1.2
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            client.domains.update_glue_record(domain, subdomain, ips)

        console.print(f"\U0001f437 Updated glue record [cyan]{subdomain}.{domain}[/cyan]")


@domains_app.command("glue-delete")
def delete_glue_record(
    domain: Annotated[str, typer.Argument(help="Domain to delete glue record from")],
    subdomain: Annotated[str, typer.Argument(help="Glue host subdomain (e.g., ns1)")],
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", "-k", envvar="PORKBUN_API_KEY", help="Porkbun API key"),
    ] = None,
    secret_key: Annotated[
        str | None,
        typer.Option("--secret-key", "-s", envvar="PORKBUN_SECRET_KEY", help="Porkbun secret key"),
    ] = None,
) -> None:
    """Delete a glue record.

    Examples:
        oinker domains glue-delete example.com ns1
    """
    with handle_errors():
        with get_client(api_key, secret_key) as client:
            client.domains.delete_glue_record(domain, subdomain)

        console.print(f"\U0001f437 Deleted glue record [cyan]{subdomain}.{domain}[/cyan]")
