# GitHub Copilot Instructions for Oinker

## Project Overview

Oinker is a delightfully Pythonic library for managing DNS at Porkbun. It provides both async (`AsyncPiglet`) and sync (`Piglet`) clients for interacting with the Porkbun API.

### Architecture

- **Async-first design**: `AsyncPiglet` is the core client; `Piglet` is a sync wrapper
- **HTTP layer**: `HttpClient` handles authentication, retries, and error translation
- **Configuration**: Credentials loaded from environment variables or constructor args
- **Exception hierarchy**: All exceptions inherit from `OinkerError` for easy catching

## Python Version and Dependencies

- **Target Python**: 3.13+ (requires Python 3.13 or later)
- **Core dependency**: httpx (async HTTP client)
- **Package manager**: uv (not pip or poetry)
- **Type checking**: ty (not mypy or pyright)
- **Linting/formatting**: ruff (replaces black, isort, flake8)

## Coding Conventions

### Type Hints

- **REQUIRED**: All functions, methods, and public APIs must have type hints
- Use `from __future__ import annotations` for forward references
- Use `TYPE_CHECKING` import guard for types only needed for type checking
- Prefer modern type syntax: `str | None` over `Optional[str]`
- Use `from collections.abc` for generic types (Mapping, Sequence, etc.)

### Dataclasses

- Use `@dataclass(frozen=True, slots=True)` for immutable data structures
- All response types should be frozen dataclasses
- Use `field()` for defaults and metadata

### String Formatting

- Use f-strings for all string formatting
- No `.format()` or `%` formatting

### Imports

- Use absolute imports from `oinker.*`
- Group imports: stdlib, third-party, local (ruff handles order automatically)
- Use `from __future__ import annotations` at the top when type hints reference the class itself

## Async/Sync Patterns

### Async Client (AsyncPiglet)

- Primary implementation in `_client.py`
- Use `httpx.AsyncClient` for HTTP calls
- All methods are async (`async def`) and awaited (`await`)
- Context manager protocol: `__aenter__` and `__aexit__`

### Sync Client (Piglet)

- Wrapper around AsyncPiglet in `_sync.py`
- Use `asyncio.run()` to execute async methods synchronously
- Keep logic in async client; sync wrapper should be thin

### Context Managers

- **REQUIRED**: Both clients must be used as context managers for proper resource cleanup
- Document context manager usage in docstrings
- Example pattern:
  ```python
  async with AsyncPiglet(api_key="...", secret_key="...") as client:
      response = await client.ping()
  ```

## Error Handling

### Exception Hierarchy

All exceptions inherit from `OinkerError`:
- `AuthenticationError`: Invalid or missing API credentials
- `AuthorizationError`: Valid credentials but not authorized
- `RateLimitError`: Rate limit exceeded (has `retry_after` attribute)
- `NotFoundError`: Domain or record not found
- `ValidationError`: Invalid record data
- `APIError`: Generic API error (has `status_code` and `message` attributes)

### Error Messages

- Be descriptive and actionable
- Use playful pig-themed language where appropriate
- Example: "Couldn't find that in the pen. Double-check the domain/record ID."

### Retry Logic

- Retry transient failures (connection errors, timeouts) automatically in `HttpClient`
- Use exponential backoff (start at 1s, double each retry)
- Default max retries: 3
- **DO NOT** auto-retry rate limits (let caller decide)

## Testing

### Test Framework

- Use pytest (not unittest)
- Enable pytest-asyncio for async tests
- Coverage required: `--cov=oinker --cov-report=term-missing`

### Test Patterns

- Use `AsyncMock(spec=httpx.AsyncClient)` for mocking HTTP client
- Test both success and error paths
- Use descriptive test names: `test_ping_returns_correct_ip_address`
- Test classes group related tests: `class TestAsyncPiglet:`
- Type hint test methods: `async def test_foo(self) -> None:`

### Mocking HTTP Responses

```python
mock_client = AsyncMock(spec=httpx.AsyncClient)
mock_client.post.return_value = httpx.Response(
    200, json={"status": "SUCCESS", "yourIp": "203.0.113.42"}
)

async with AsyncPiglet(api_key="test", secret_key="test", _http_client=mock_client) as piglet:
    result = await piglet.ping()
```

### Test Coverage

- Aim for high coverage but don't chase 100%
- Exclude patterns (in pyproject.toml):
  - `pragma: no cover`
  - `if TYPE_CHECKING:`
  - `raise NotImplementedError`

## Documentation

### Docstrings

- **REQUIRED**: All public functions, methods, and classes must have docstrings
- Use Google-style docstrings (not NumPy or reStructuredText)
- Include Args, Returns, Raises sections as appropriate
- Example:
  ```python
  async def ping(self) -> PingResponse:
      """Test API connectivity and authentication.

      Returns:
          PingResponse with your public IP address.

      Raises:
          AuthenticationError: If credentials are invalid.
          APIError: If the request fails.
      """
  ```

### Module Docstrings

- Start each module with a brief docstring explaining its purpose
- Example: `"""HTTP layer with retry logic for oinker."""`

## Configuration

### Credentials

- Support two methods (in priority order):
  1. Constructor arguments: `AsyncPiglet(api_key="...", secret_key="...")`
  2. Environment variables: `PORKBUN_API_KEY` and `PORKBUN_SECRET_KEY`
- Load from environment in `OinkerConfig.__post_init__`
- Never log or expose credentials

### Constants

- Use `typing.Final` for module-level constants
- ALL_CAPS naming for constants
- Group related constants together

## Code Quality

### Linting and Formatting

- Run `make lint` to check (uses ruff)
- Run `make format` to auto-format (uses ruff)
- Run `make fix` to auto-fix issues and format
- Ruff config in pyproject.toml:
  - Line length: 100
  - Selected rules: E, F, I, UP, B, SIM, ASYNC

### Type Checking

- Run `make typecheck` (uses ty, not mypy/pyright)
- All code must pass type checking
- No `# type: ignore` without good reason

### Running Tests

- `make test`: Run tests with coverage
- `make test-cov`: Generate HTML coverage report
- `make check`: Run lint, format-check, typecheck, and test

## API Design Principles

1. **Pythonic**: Use context managers, native types, and familiar patterns
2. **Async-first**: AsyncPiglet is primary; Piglet is a convenience wrapper
3. **Type-safe**: Full type hints for autocomplete and error checking
4. **Explicit errors**: Clear exception hierarchy with descriptive messages
5. **Sensible defaults**: Credentials from environment, reasonable timeouts
6. **Resource cleanup**: Use context managers for proper HTTP client cleanup
7. **Retry resilience**: Auto-retry transient failures with backoff

## Common Patterns

### Adding a New API Method

1. Add response type as frozen dataclass in `_types.py`
2. Implement async method in `AsyncPiglet` class
3. Add docstring with Args, Returns, Raises
4. Sync wrapper in `Piglet` will use it automatically
5. Export types in `__init__.py`'s `__all__`
6. Add tests for success and error cases

### Adding a New Exception Type

1. Inherit from `OinkerError` in `_exceptions.py`
2. Add docstring with pig-themed message
3. Add custom attributes if needed (like `retry_after` on `RateLimitError`)
4. Export in `__init__.py`'s `__all__`
5. Raise from appropriate location in `HttpClient._handle_response()`

## Things to Avoid

- ❌ Blocking calls in async functions (use async libraries)
- ❌ `Optional[T]` syntax (use `T | None`)
- ❌ `.format()` or `%` string formatting (use f-strings)
- ❌ Mutable default arguments
- ❌ Bare `except:` clauses
- ❌ Type: ignore comments without explanation
- ❌ Adding new linters/formatters (we use ruff for everything)
- ❌ pip/poetry commands (we use uv)
