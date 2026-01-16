"""Pricing CLI subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from oinker._exceptions import OinkerError
from oinker.cli._utils import console, err_console
from oinker.pricing import get_pricing_sync

pricing_app = typer.Typer(
    name="pricing",
    help="View TLD pricing information.",
    no_args_is_help=False,
)


@pricing_app.command("list")
def list_pricing(
    tld: Annotated[
        str | None,
        typer.Option("--tld", "-t", help="Filter by specific TLD (e.g., 'com', 'net')"),
    ] = None,
    sort_by: Annotated[
        str,
        typer.Option(
            "--sort",
            "-s",
            help="Sort by: tld, registration, renewal, transfer",
        ),
    ] = "tld",
    limit: Annotated[
        int | None,
        typer.Option("--limit", "-l", help="Limit number of results"),
    ] = None,
) -> None:
    """List domain pricing for all TLDs.

    Shows registration, renewal, and transfer prices. No authentication required.

    Examples:
        oinker pricing list
        oinker pricing list --tld com
        oinker pricing list --sort registration --limit 20
    """
    try:
        pricing = get_pricing_sync()

        if tld:
            tld_lower = tld.lower().lstrip(".")
            if tld_lower not in pricing:
                err_console.print(
                    f"\U0001f437 Oops! TLD '.{tld_lower}' not found",
                    style="bold red",
                )
                raise typer.Exit(code=1)
            pricing = {tld_lower: pricing[tld_lower]}

        items = list(pricing.values())
        if sort_by == "registration":
            items.sort(key=lambda x: float(x.registration) if x.registration else 999999)
        elif sort_by == "renewal":
            items.sort(key=lambda x: float(x.renewal) if x.renewal else 999999)
        elif sort_by == "transfer":
            items.sort(key=lambda x: float(x.transfer) if x.transfer else 999999)
        else:
            items.sort(key=lambda x: x.tld)

        if limit:
            items = items[:limit]

        table = Table(title="\U0001f437 TLD Pricing")
        table.add_column("TLD", style="cyan")
        table.add_column("Registration", style="green", justify="right")
        table.add_column("Renewal", style="yellow", justify="right")
        table.add_column("Transfer", style="magenta", justify="right")

        for item in items:
            table.add_row(
                f".{item.tld}",
                f"${item.registration}",
                f"${item.renewal}",
                f"${item.transfer}",
            )

        console.print(table)
        console.print(f"\n\U0001f437 Showing {len(items)} TLDs")
    except OinkerError as e:
        err_console.print(f"\U0001f437 Oops! {e}", style="bold red")
        raise typer.Exit(code=1) from None


@pricing_app.callback(invoke_without_command=True)
def pricing_callback(ctx: typer.Context) -> None:
    """Handle 'oinker pricing' without subcommand - show list by default."""
    if ctx.invoked_subcommand is None:
        list_pricing(tld=None, sort_by="tld", limit=None)
