"""Tests for oinker exception hierarchy."""

from __future__ import annotations

import pytest

from oinker import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    OinkerError,
    RateLimitError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test that all exceptions inherit from OinkerError."""

    @pytest.mark.parametrize(
        "exception_class",
        [
            AuthenticationError,
            AuthorizationError,
            RateLimitError,
            NotFoundError,
            ValidationError,
            APIError,
        ],
    )
    def test_inherits_from_oinker_error(self, exception_class: type[OinkerError]) -> None:
        """All custom exceptions should inherit from OinkerError."""
        assert issubclass(exception_class, OinkerError)

    def test_can_catch_all_with_base_class(self) -> None:
        """Catching OinkerError should catch all subclasses."""
        exceptions = [
            AuthenticationError("test"),
            AuthorizationError("test"),
            RateLimitError("test"),
            NotFoundError("test"),
            ValidationError("test"),
            APIError("test"),
        ]

        for exc in exceptions:
            with pytest.raises(OinkerError):
                raise exc


class TestRateLimitError:
    """Tests for RateLimitError with retry_after."""

    def test_with_retry_after(self) -> None:
        """RateLimitError should store retry_after value."""
        exc = RateLimitError("Too many requests", retry_after=30.0)
        assert exc.retry_after == 30.0
        assert str(exc) == "Too many requests"

    def test_without_retry_after(self) -> None:
        """RateLimitError should handle missing retry_after."""
        exc = RateLimitError("Too many requests")
        assert exc.retry_after is None


class TestAPIError:
    """Tests for APIError with status_code."""

    def test_with_status_code(self) -> None:
        """APIError should store status_code and message."""
        exc = APIError("Server error", status_code=500)
        assert exc.status_code == 500
        assert exc.message == "Server error"
        assert str(exc) == "Server error"

    def test_without_status_code(self) -> None:
        """APIError should handle missing status_code."""
        exc = APIError("Unknown error")
        assert exc.status_code is None
        assert exc.message == "Unknown error"
