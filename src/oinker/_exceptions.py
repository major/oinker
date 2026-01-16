"""Exception hierarchy for oinker.

All oinker-specific exceptions inherit from OinkerError for easy catching.
"""

from __future__ import annotations


class OinkerError(Exception):
    """Base exception for all oinker errors.

    Catch this to handle any oinker-related error.
    """


class AuthenticationError(OinkerError):
    """Invalid or missing API credentials.

    Oops! Couldn't authenticate. Check your API keys aren't hogwash.
    """


class AuthorizationError(OinkerError):
    """Valid credentials but not authorized for this domain/action.

    You're authenticated, but this pen isn't yours to root around in.
    """


class RateLimitError(OinkerError):
    """Rate limit exceeded.

    Whoa there! Slow your trot. Try again later.
    """

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        """Initialize with optional retry delay.

        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying.
        """
        super().__init__(message)
        self.retry_after = retry_after


class NotFoundError(OinkerError):
    """Domain or record not found.

    Couldn't find that in the pen. Double-check the domain/record ID.
    """


class ValidationError(OinkerError):
    """Invalid record data.

    That data doesn't pass the sniff test. Check your input.
    """


class APIError(OinkerError):
    """Generic API error with status code and message.

    Something went wrong at the farm. Check the details.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize with status code.

        Args:
            message: Error message from the API.
            status_code: HTTP status code if available.
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message
