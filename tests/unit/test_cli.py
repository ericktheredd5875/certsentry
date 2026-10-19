from typer.testing import CliRunner

from certsentry import __version__
from certsentry.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_check_is_a_stub() -> None:
    result = runner.invoke(app, ["check", "example.com"])
    assert result.exit_code == 4
