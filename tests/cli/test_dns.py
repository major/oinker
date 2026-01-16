"""Tests for DNS CLI subcommands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from oinker import AuthenticationError, NotFoundError, Piglet
from oinker.cli._main import app
from oinker.dns import DNSRecordResponse

runner = CliRunner()


class TestDNSListCommand:
    """Tests for dns list command."""

    def test_list_records_success(self) -> None:
        """dns list should display records in a table."""
        mock_records = [
            DNSRecordResponse(
                id="123456",
                name="example.com",
                record_type="A",
                content="1.2.3.4",
                ttl=600,
                priority=0,
            ),
            DNSRecordResponse(
                id="123457",
                name="www.example.com",
                record_type="A",
                content="1.2.3.4",
                ttl=600,
                priority=0,
            ),
        ]
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.list.return_value = mock_records
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "list", "example.com"])

        assert result.exit_code == 0
        assert "123456" in result.output
        assert "example.com" in result.output
        assert "1.2.3.4" in result.output

    def test_list_records_empty(self) -> None:
        """dns list should show message when no records found."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.list.return_value = []
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "list", "example.com"])

        assert result.exit_code == 0
        assert "No records found" in result.output

    def test_list_records_shows_priority_for_mx(self) -> None:
        """dns list should show priority for MX records."""
        mock_records = [
            DNSRecordResponse(
                id="123456",
                name="example.com",
                record_type="MX",
                content="mail.example.com",
                ttl=600,
                priority=10,
            ),
        ]
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.list.return_value = mock_records
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "list", "example.com"])

        assert result.exit_code == 0
        assert "10" in result.output


class TestDNSCreateCommand:
    """Tests for dns create command."""

    def test_create_a_record(self) -> None:
        """dns create should create an A record."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.create.return_value = "123456"
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "create", "example.com", "A", "www", "1.2.3.4"])

        assert result.exit_code == 0
        assert "Squeee!" in result.output
        assert "123456" in result.output
        mock_client.dns.create.assert_called_once()

    def test_create_with_custom_ttl(self) -> None:
        """dns create --ttl should set custom TTL."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.create.return_value = "123456"
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(
                app, ["dns", "create", "example.com", "A", "www", "1.2.3.4", "--ttl", "3600"]
            )

        assert result.exit_code == 0
        call_args = mock_client.dns.create.call_args
        record = call_args[0][1]
        assert record.ttl == 3600

    def test_create_mx_with_priority(self) -> None:
        """dns create MX --priority should set custom priority."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.create.return_value = "123456"
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(
                app,
                [
                    "dns",
                    "create",
                    "example.com",
                    "MX",
                    "@",
                    "mail.example.com",
                    "--priority",
                    "20",
                ],
            )

        assert result.exit_code == 0
        call_args = mock_client.dns.create.call_args
        record = call_args[0][1]
        assert record.priority == 20

    def test_create_at_root_domain(self) -> None:
        """dns create with @ should create record at root."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.create.return_value = "123456"
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "create", "example.com", "A", "@", "1.2.3.4"])

        assert result.exit_code == 0
        call_args = mock_client.dns.create.call_args
        record = call_args[0][1]
        assert record.name is None

    def test_create_unsupported_type(self) -> None:
        """dns create should reject unsupported record types."""
        result = runner.invoke(app, ["dns", "create", "example.com", "FAKE", "www", "value"])

        assert result.exit_code == 1
        assert "Unsupported record type" in result.output

    def test_create_validation_error(self) -> None:
        """dns create should show error on invalid record data."""
        result = runner.invoke(app, ["dns", "create", "example.com", "A", "www", "bad-ip"])

        assert result.exit_code == 1
        assert "Invalid IPv4" in result.output


class TestDNSDeleteCommand:
    """Tests for dns delete command."""

    def test_delete_by_id(self) -> None:
        """dns delete --id should delete record by ID."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "delete", "example.com", "--id", "123456"])

        assert result.exit_code == 0
        assert "Gobbled up record 123456" in result.output
        mock_client.dns.delete.assert_called_once_with("example.com", record_id="123456")

    def test_delete_by_type_and_name(self) -> None:
        """dns delete --type --name should delete by type and name."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(
                app, ["dns", "delete", "example.com", "--type", "A", "--name", "www"]
            )

        assert result.exit_code == 0
        assert "Gobbled up all A records" in result.output
        mock_client.dns.delete_by_name_type.assert_called_once()

    def test_delete_at_root_domain(self) -> None:
        """dns delete --name @ should delete records at root."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(
                app, ["dns", "delete", "example.com", "--type", "A", "--name", "@"]
            )

        assert result.exit_code == 0
        assert "Gobbled up all A records for root" in result.output
        mock_client.dns.delete_by_name_type.assert_called_once_with("example.com", "A", "")

    def test_delete_missing_args(self) -> None:
        """dns delete should error without --id or --type/--name."""
        result = runner.invoke(app, ["dns", "delete", "example.com"])

        assert result.exit_code == 1
        assert "Provide --id or both --type and --name" in result.output

    def test_delete_not_found(self) -> None:
        """dns delete should show error when record not found."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.delete.side_effect = NotFoundError("Record not found")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "delete", "example.com", "--id", "999999"])

        assert result.exit_code == 1
        assert "Record not found" in result.output

    def test_delete_auth_error(self) -> None:
        """dns delete should show error on authentication failure."""
        mock_client = MagicMock(spec=Piglet)
        mock_client.dns.delete.side_effect = AuthenticationError("Invalid API key")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("oinker.cli._utils.Piglet", return_value=mock_client):
            result = runner.invoke(app, ["dns", "delete", "example.com", "--id", "123456"])

        assert result.exit_code == 1
        assert "Invalid API key" in result.output
