import csv
import json
import sys
from enum import StrEnum
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from dartfx.dataverse.dataverse import (
    DataverseServer,
    SearchParameters,
    ServerInstallation,
    fetch_dataverse_installations,
)

app = typer.Typer(
    name="dartfx-dataverse",
    help="CLI for discovering and interacting with Dataverse repositories.",
    add_completion=False,
)
console = Console()


class OutputFormat(StrEnum):
    TABLE = "table"
    JSON = "json"
    CSV = "csv"


def get_server(hostname: str, api_key: str | None = None) -> DataverseServer:
    """Helper to create a DataverseServer instance."""
    installation = ServerInstallation(hostname=hostname)
    return DataverseServer(server=installation, api_key=api_key)


@app.command()
def installations(
    format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.TABLE,
    limit: Annotated[int | None, typer.Option("--limit", "-l", help="Limit the number of results")] = None,
) -> None:
    """List worldwide Dataverse installations."""
    with console.status("[bold green]Fetching installations..."):
        all_installations = fetch_dataverse_installations()

    if limit:
        all_installations = all_installations[:limit]

    if format == OutputFormat.JSON:
        console.print_json(json.dumps([inst.model_dump(exclude_none=True) for inst in all_installations]))
        return

    if format == OutputFormat.CSV:
        writer = csv.DictWriter(sys.stdout, fieldnames=["name", "hostname", "country", "launch_year"])
        writer.writeheader()
        for inst in all_installations:
            writer.writerow(
                {
                    "name": inst.name or "",
                    "hostname": inst.hostname or "",
                    "country": inst.country or "",
                    "launch_year": inst.launch_year or "",
                }
            )
        return

    table = Table(title="Worldwide Dataverse Installations")
    table.add_column("Name", style="cyan")
    table.add_column("Hostname", style="magenta")
    table.add_column("Country", style="green")
    table.add_column("Launch Year", style="yellow")

    for inst in all_installations:
        table.add_row(
            inst.name or "N/A",
            inst.hostname or "N/A",
            inst.country or "N/A",
            inst.launch_year or "N/A",
        )

    console.print(table)


@app.command()
def info(
    hostname: Annotated[str, typer.Argument(help="Dataverse server hostname")],
    api_key: Annotated[str | None, typer.Option("--api-key", "-k", envvar="DATAVERSE_API_KEY", help="API Key")] = None,
) -> None:
    """Get information about a specific Dataverse server."""
    server = get_server(hostname, api_key)
    with console.status(f"[bold green]Fetching info from {hostname}..."):
        try:
            version_info = server.get_info_version()
            server_info = server.get_info_server()
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise typer.Exit(code=1) from e

    console.print(f"[bold cyan]Server:[/] {server_info.get('data', {}).get('message', 'N/A')}")
    console.print(f"[bold cyan]Version:[/] {version_info.get('data', {}).get('version', 'N/A')}")
    console.print(f"[bold cyan]Build:[/] {version_info.get('data', {}).get('build', 'N/A')}")


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    hostname: Annotated[
        str, typer.Option("--hostname", "-H", help="Dataverse server hostname")
    ] = "dataverse.harvard.edu",
    type: Annotated[str | None, typer.Option("--type", "-t", help="Type of object (dataverse, dataset, file)")] = None,
    limit: Annotated[
        int, typer.Option("--per-page", "--limit", "-p", "-l", help="Limit the number of results per page")
    ] = 25,
    sort: Annotated[str | None, typer.Option("--sort", "-s", help="Sort field (name, date)")] = None,
    order: Annotated[str | None, typer.Option("--order", "-o", help="Sort order (asc, desc)")] = None,
    format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.TABLE,
    api_key: Annotated[str | None, typer.Option("--api-key", "-k", envvar="DATAVERSE_API_KEY", help="API Key")] = None,
) -> None:
    """Search for dataverses, datasets, and files."""
    server = get_server(hostname, api_key)
    params = SearchParameters(q=query, type=type, per_page=limit, sort=sort, order=order)

    with console.status(f"[bold green]Searching {hostname} for '{query}'..."):
        try:
            results = server.search(params)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise typer.Exit(code=1) from e

    if format == OutputFormat.JSON:
        console.print_json(data=results)
        return

    items = results.get("data", {}).get("items", [])

    if format == OutputFormat.CSV:
        writer = csv.DictWriter(sys.stdout, fieldnames=["type", "name", "identifier", "published_at"])
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "type": item.get("type", ""),
                    "name": item.get("name") or item.get("title") or "",
                    "identifier": item.get("global_id") or item.get("identifier") or "",
                    "published_at": item.get("published_at") or "",
                }
            )
        return

    items = results.get("data", {}).get("items", [])
    total = results.get("data", {}).get("total_count", 0)

    table = Table(title=f"Search Results for '{query}' (Total: {total})")
    table.add_column("Type", style="dim")
    table.add_column("Name/Title", style="cyan")
    table.add_column("Identifier", style="magenta")
    table.add_column("Published", style="green")

    for item in items:
        item_type = item.get("type", "unknown")
        name = item.get("name") or item.get("title") or "N/A"
        identifier = item.get("global_id") or item.get("identifier") or "N/A"
        published = item.get("published_at") or "N/A"

        table.add_row(item_type, name, identifier, published)

    console.print(table)


@app.command()
def metadatablocks(
    hostname: Annotated[str, typer.Argument(help="Dataverse server hostname")],
    format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.TABLE,
    api_key: Annotated[str | None, typer.Option("--api-key", "-k", envvar="DATAVERSE_API_KEY", help="API Key")] = None,
) -> None:
    """List metadata blocks for a specific Dataverse server."""
    server = get_server(hostname, api_key)
    with console.status(f"[bold green]Fetching metadata blocks from {hostname}..."):
        try:
            blocks = server.get_metadatablocks()
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise typer.Exit(code=1) from e

    data = blocks.get("data", [])

    if format == OutputFormat.CSV:
        writer = csv.DictWriter(sys.stdout, fieldnames=["name", "displayName"])
        writer.writeheader()
        for block in data:
            writer.writerow(
                {
                    "name": block.get("name", ""),
                    "displayName": block.get("displayName", ""),
                }
            )
        return

    table = Table(title=f"Metadata Blocks for {hostname}")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="magenta")

    for block in blocks.get("data", []):
        table.add_row(block.get("name", "N/A"), block.get("displayName", "N/A"))

    console.print(table)


if __name__ == "__main__":
    app()
