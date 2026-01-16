"""Tests for CLI main commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from oinker import AuthenticationError, Piglet, PingResponse
from oinker.cli._main import app

runner = CliRunner()


class TestPingCommand:
    """Tests for the ping command."""

    def test_ping_success(self) -> None:
        """ping should display success message and IP on valid credentials."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.ping.return_value = PingResponse(your_ip="203.0.113.42")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["ping"])

        assert result.exit_code == 0
        assert "Oink! Connected successfully" in result.output
        assert "203.0.113.42" in result.output

    def test_ping_auth_error(self) -> None:
        """ping should show error message on authentication failure."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.ping.side_effect = AuthenticationError("Invalid credentials")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["ping"])

        assert result.exit_code == 1
        assert "Oops!" in result.output
        assert "Invalid credentials" in result.output

    def test_ping_passes_credentials(self) -> None:
        """ping should pass API key and secret to client."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.ping.return_value = PingResponse(your_ip="1.2.3.4")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client) as mock_piglet:
            runner.invoke(app, ["ping", "--api-key", "pk1_test", "--secret-key", "sk1_test"])

        mock_piglet.assert_called_once_with(api_key="pk1_test", secret_key="sk1_test")


class TestAppHelp:
    """Tests for the main app help."""

    def test_help_shows_description(self) -> None:
        """--help should show the app description."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Porkbun" in result.output
        assert "DNS" in result.output

    def test_no_args_shows_help(self) -> None:
        """Running with no args should show help content."""
        result = runner.invoke(app, [])

        # Typer returns exit code 2 for no-args-is-help
        assert "ping" in result.output
        assert "dns" in result.output
