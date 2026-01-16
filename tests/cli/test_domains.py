"""Tests for domains CLI subcommands."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from oinker import AuthenticationError, NotFoundError
from oinker.cli._main import app
from oinker.domains import DomainInfo

runner = CliRunner()


class TestDomainsListCommand:
    """Tests for domains list command."""

    def test_list_domains_success(self, mock_piglet_client: MagicMock) -> None:
        """domains list should display domains in a table."""
        mock_domains = [
            DomainInfo(
                domain="example.com",
                status="ACTIVE",
                tld="com",
                create_date=datetime(2024, 1, 1, 12, 0, 0),
                expire_date=datetime(2025, 1, 1, 12, 0, 0),
                security_lock=True,
                whois_privacy=True,
                auto_renew=True,
                not_local=False,
                labels=(),
            ),
            DomainInfo(
                domain="example.org",
                status="ACTIVE",
                tld="org",
                create_date=datetime(2024, 6, 1, 12, 0, 0),
                expire_date=datetime(2025, 6, 1, 12, 0, 0),
                security_lock=False,
                whois_privacy=False,
                auto_renew=False,
                not_local=False,
                labels=(),
            ),
        ]
        mock_piglet_client.domains.list.return_value = mock_domains

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "list"])

        assert result.exit_code == 0
        assert "example.com" in result.output
        assert "example.org" in result.output
        assert "ACTIVE" in result.output
        assert "2025-01-01" in result.output

    def test_list_domains_empty(self, mock_piglet_client: MagicMock) -> None:
        """domains list should show message when no domains found."""
        mock_piglet_client.domains.list.return_value = []

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "list"])

        assert result.exit_code == 0
        assert "No domains found" in result.output

    def test_list_domains_auth_error(self, mock_piglet_client: MagicMock) -> None:
        """domains list should show error on authentication failure."""
        mock_piglet_client.domains.list.side_effect = AuthenticationError("Invalid API key")

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "list"])

        assert result.exit_code == 1
        assert "Invalid API key" in result.output


class TestDomainsNameserversCommand:
    """Tests for domains nameservers command."""

    def test_get_nameservers_success(self, mock_piglet_client: MagicMock) -> None:
        """domains nameservers should display nameservers."""
        mock_nameservers = ["ns1.porkbun.com", "ns2.porkbun.com"]
        mock_piglet_client.domains.get_nameservers.return_value = mock_nameservers

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "nameservers", "example.com"])

        assert result.exit_code == 0
        assert "ns1.porkbun.com" in result.output
        assert "ns2.porkbun.com" in result.output
        assert "example.com" in result.output

    def test_get_nameservers_empty(self, mock_piglet_client: MagicMock) -> None:
        """domains nameservers should show message when no nameservers found."""
        mock_piglet_client.domains.get_nameservers.return_value = []

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "nameservers", "example.com"])

        assert result.exit_code == 0
        assert "No nameservers found" in result.output

    def test_get_nameservers_not_found(self, mock_piglet_client: MagicMock) -> None:
        """domains nameservers should show error when domain not found."""
        mock_piglet_client.domains.get_nameservers.side_effect = NotFoundError("Domain not found")

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "nameservers", "unknown.com"])

        assert result.exit_code == 1
        assert "Domain not found" in result.output

    def test_get_nameservers_auth_error(self, mock_piglet_client: MagicMock) -> None:
        """domains nameservers should show error on authentication failure."""
        mock_piglet_client.domains.get_nameservers.side_effect = AuthenticationError(
            "Invalid API key"
        )

        with patch("oinker.cli._utils.Piglet", return_value=mock_piglet_client):
            result = runner.invoke(app, ["domains", "nameservers", "example.com"])

        assert result.exit_code == 1
        assert "Invalid API key" in result.output
