# Oinker - Agent Guidelines

A Pythonic library for managing DNS at Porkbun. Python 3.13+, async-first design.

## Quick Reference

```bash
# Install dependencies
uv sync --dev

# Run all checks (lint, format, typecheck, test)
make check

# Individual commands
make lint          # ruff check .
make format        # ruff format .
make typecheck     # ty check
make test          # pytest with coverage

# Run single test file
uv run pytest tests/test_client.py

# Run single test by name
uv run pytest -k "test_ping"

# Run tests in a class
uv run pytest tests/dns/test_records.py::TestARecord

# Fix lint issues automatically
make fix
```

## Project Structure

```
src/oinker/
├── __init__.py          # Public API exports
├── _client.py           # AsyncPiglet (async client)
├── _sync.py             # Piglet (sync wrapper)
├── _http.py             # HTTP layer with retry logic
├── _config.py           # Configuration and auth
├── _exceptions.py       # Exception hierarchy
├── _types.py            # Shared dataclasses
├── dns/
│   ├── _api.py          # AsyncDNSAPI operations
│   ├── _sync.py         # SyncDNSAPI wrapper
│   └── _records.py      # DNS record dataclasses
├── dnssec/
│   ├── _api.py          # AsyncDNSSECAPI operations
│   ├── _sync.py         # SyncDNSSECAPI wrapper
│   └── _types.py        # DNSSEC record dataclasses
├── domains/
│   ├── _api.py          # AsyncDomainsAPI operations
│   ├── _sync.py         # SyncDomainsAPI wrapper
│   └── _types.py        # Domain dataclasses
└── ssl/
    ├── _api.py          # AsyncSSLAPI operations
    ├── _sync.py         # SyncSSLAPI wrapper
    └── _types.py        # SSL bundle dataclass
```

## Code Style

### General Principles

- **Async-first**: Core logic in async, sync wrappers use `asyncio.run_until_complete()`
- **Dataclasses over Pydantic**: Use `@dataclass(frozen=True, slots=True)` for immutable data
- **Type hints everywhere**: Full type annotations, no `Any` unless unavoidable
- **Single-purpose functions**: Small, focused, testable

### Imports

```python
# Standard library first, then third-party, then local
from __future__ import annotations  # Always first

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

from oinker._config import OinkerConfig
from oinker._exceptions import APIError

# Use TYPE_CHECKING for import-only types to avoid circular imports
if TYPE_CHECKING:
    from types import TracebackType
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `AsyncPiglet`, `DNSRecordResponse` |
| Functions/methods | snake_case | `get_by_name_type()` |
| Constants | SCREAMING_SNAKE | `DEFAULT_TIMEOUT`, `BASE_URL` |
| Private | Leading underscore | `_validate_ttl()`, `_http` |
| Type aliases | PascalCase | `DNSRecordType`, `DNSRecord` |

### Dataclasses

```python
@dataclass(frozen=True, slots=True)  # Immutable + memory efficient
class PingResponse:
    """Response from the ping endpoint.

    Attributes:
        your_ip: The client's public IP address as seen by Porkbun.
    """
    your_ip: str

# For mutable records with validation:
@dataclass(slots=True)
class ARecord:
    record_type: ClassVar[DNSRecordType] = "A"
    content: str
    name: str | None = None
    ttl: int = 600

    def __post_init__(self) -> None:
        """Validate on construction."""
        ip = _validate_ipv4(self.content)
        object.__setattr__(self, "content", str(ip))
```

### Error Handling

- Custom exceptions inherit from `OinkerError` base class
- Descriptive messages with context
- Re-raise with `from e` to preserve stack traces

```python
class AuthenticationError(OinkerError):
    """Invalid or missing API credentials."""

# Usage:
try:
    return IPv4Address(value)
except AddressValueError as e:
    msg = f"Invalid IPv4 address: {value}"
    raise ValidationError(msg) from e
```

### Docstrings (PEP 257 Google style)

```python
async def create(self, domain: str, record: DNSRecord) -> str:
    """Create a new DNS record.

    Args:
        domain: The domain name (e.g., "example.com").
        record: The DNS record to create.

    Returns:
        The ID of the created record.

    Raises:
        AuthenticationError: If credentials are invalid.
        ValidationError: If record data is invalid.
        APIError: If the request fails.
    """
```

### Type Annotations

```python
# Union types use | (Python 3.10+)
def __init__(self, api_key: str | None = None) -> None: ...

# Generic types use builtins
async def list(self, domain: str) -> list[DNSRecordResponse]: ...

# Use Literal for constrained strings
DNSRecordType = Literal["A", "AAAA", "MX", "CNAME", ...]

# Use Final for constants
BASE_URL: Final[str] = "https://api.porkbun.com/api/json/v3"
```

## Testing Patterns

### Async Tests

pytest-asyncio with `asyncio_mode = "auto"` - no decorators needed:

```python
class TestAsyncPiglet:
    async def test_ping(self) -> None:
        """ping() should return PingResponse with IP."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = httpx.Response(
            200, json={"status": "SUCCESS", "yourIp": "1.2.3.4"}
        )

        async with AsyncPiglet(
            api_key="test", secret_key="test", _http_client=mock_client
        ) as piglet:
            result = await piglet.ping()

        assert isinstance(result, PingResponse)
```

### Parameterized Tests

```python
@pytest.mark.parametrize(
    ("content", "expected_valid"),
    [
        ("1.2.3.4", True),
        ("not-an-ip", False),
    ],
)
def test_ipv4_validation(self, content: str, expected_valid: bool) -> None:
    expectation = nullcontext() if expected_valid else pytest.raises(ValidationError)
    with expectation:
        ARecord(content=content)
```

### Fixtures (conftest.py)

```python
@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx.AsyncClient for testing."""
    return AsyncMock(spec=httpx.AsyncClient)  # spec validates attrs
```

## Ruff Configuration

```toml
[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "ASYNC"]
```

- **E/F**: pyflakes + pycodestyle errors
- **I**: isort import sorting
- **UP**: pyupgrade (modern Python syntax)
- **B**: bugbear (common pitfalls)
- **SIM**: simplify (code simplification)
- **ASYNC**: async best practices

## Type Checking

Uses `ty` (not mypy/pyright):

```bash
uv run ty check
```

## Key Design Patterns

1. **Dependency injection for testing**: `_http_client` parameter allows mock injection
2. **Context managers**: Both sync and async clients support `with`/`async with`
3. **Validation in `__post_init__`**: Records validate themselves on construction
4. **ClassVar for shared attributes**: `record_type: ClassVar[DNSRecordType] = "A"`
5. **Frozen dataclasses**: Use `object.__setattr__` when mutation needed in `__post_init__`
