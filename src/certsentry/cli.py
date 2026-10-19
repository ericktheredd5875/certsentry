"""Command-line interface. Parses arguments and delegates to the core."""

from typing import Annotated

import typer

from certsentry import __version__

app = typer.Typer(help="Audit TLS certificates for a list of domains.", no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"certsentry {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show version."),
    ] = False,
) -> None:
    """Audit TLS certificates for a list of domains."""


@app.command()
def check(targets: Annotated[list[str], typer.Argument(help="host or host:port")]) -> None:
    """Check the certificates of TARGETS (not implemented yet)."""
    typer.echo("not implemented yet", err=True)
    raise typer.Exit(code=4)
