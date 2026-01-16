# GitHub Copilot Code Review Instructions

## Review Philosophy: Invert, Always Invert

Apply Charlie Munger's inversion principle: Instead of asking "Is this code good?", ask **"What would make this code fail?"**

Focus on preventing failure rather than achieving brilliance:
- What edge cases would break this?
- What would cause this to fail in production?
- What would make this unmaintainable in 6 months?
- What security holes does this open?

When something could fail, explain **HOW** it would fail and suggest the prevention.

---

## Project Context: Oinker

Async-first Porkbun DNS client library. Python 3.13+.

### Tech Stack
- **HTTP**: httpx (async)
- **Type checking**: ty
- **Linting/Formatting**: ruff
- **Testing**: pytest + pytest-asyncio
- **Package manager**: uv

### Architecture Patterns
- Async-first: Core logic in async, sync wrappers use `loop.run_until_complete()`
- Dataclasses over Pydantic: `@dataclass(frozen=True, slots=True)`
- Exception hierarchy: All exceptions inherit from `OinkerError`
- Validation in `__post_init__`: Records validate themselves on construction

---

## Inversion Checklists by File Type

### Source Code (`src/oinker/**/*.py`)

**Architecture failures to prevent:**
- Blocking calls in async functions (use httpx, not requests)
- Missing context manager cleanup (`__aexit__` must close resources)
- Sync wrappers not using `loop.run_until_complete()` correctly

**API design failures to prevent:**
- Breaking the async-first pattern (core logic must be async)
- Inconsistent naming (methods: snake_case, classes: PascalCase)
- Missing type hints (full annotations required, avoid `Any`)
- Pydantic usage (prefer dataclasses)

**HTTP/Network failures to prevent:**
- Missing retry logic for transient failures
- No timeout on HTTP requests
- Swallowing exceptions instead of re-raising with context
- Not preserving exception chains (use `from e`)

**Validation failures to prevent:**
- Records accepting invalid data (validate in `__post_init__`)
- TTL below 600 seconds (Porkbun minimum)
- Invalid IP addresses passing through

**Exception handling failures to prevent:**
- Generic `except` clauses hiding real errors
- Error messages too vague for debugging
- Not using the `OinkerError` hierarchy

### HTTP Layer (`src/oinker/_http.py`)

**What would cause network operations to fail?**
- No exponential backoff on retries
- Retrying non-idempotent operations
- Missing timeout configuration
- Not handling `httpx.ConnectError`, `httpx.TimeoutException`
- Rate limit responses (429) not surfaced as `RateLimitError`

### Configuration (`src/oinker/_config.py`)

**What would cause auth to fail?**
- Credentials not loaded from environment when not provided
- No validation that both `api_key` and `secret_key` are present
- Sensitive data logged or exposed in exceptions

### DNS Records (`src/oinker/dns/**/*.py`)

**What would cause DNS operations to fail?**
- Record dataclasses not validating content on init
- IPv4/IPv6 addresses not validated
- `ClassVar[DNSRecordType]` not set on record classes
- `from_api_response()` not handling missing/malformed fields
- Priority validation missing for MX/SRV records

### Tests (`tests/**/*.py`)

**What would make these tests meaningless?**
- Tests that pass but don't assert meaningful outcomes
- Mocks without `spec=` (won't catch attribute errors)
- Missing edge cases: empty responses, network errors, invalid data
- Not testing both success and failure paths
- Parameterized tests with boolean flags instead of `nullcontext()`/`pytest.raises()`

**Preferred pattern:**
```python
@pytest.mark.parametrize(("input", "valid"), [("good", True), ("bad", False)])
def test_validation(self, input: str, valid: bool) -> None:
    expectation = nullcontext() if valid else pytest.raises(ValidationError)
    with expectation:
        SomeRecord(content=input)
```

### Test Fixtures (`tests/conftest.py`)

**What would make fixtures unreliable?**
- Fixtures without proper cleanup
- `AsyncMock` without `spec=httpx.AsyncClient`
- Fixtures returning mutable state shared across tests

### Project Config (`pyproject.toml`)

**What would break the build/test cycle?**
- Missing dev dependencies
- Incompatible version constraints
- pytest-asyncio missing `asyncio_mode = "auto"`
- Coverage excluding important paths

### CI Workflows (`.github/workflows/**`)

**What would cause CI to give false confidence?**
- Not testing all supported Python versions (3.13, 3.14)
- Missing typecheck step (`ty check`)
- Secrets exposed in logs
- Caching that hides dependency issues

### Makefile

**What would make the Makefile unreliable?**
- Missing `.PHONY` declarations
- Commands that fail silently
- Inconsistency between Makefile and CI commands

---

## What NOT to Review

Don't nitpick these—automated tools handle them:
- **Style issues**: ruff handles formatting and linting
- **Type errors**: ty handles type checking
- **Import order**: ruff's isort handles this

Focus review time on logic, architecture, and failure modes.
