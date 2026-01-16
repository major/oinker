# 🐷 Oinker - Project Plan

> *DNS management that doesn't stink!*

A delightfully Pythonic library for managing DNS at Porkbun. Async-first with sync wrappers, type-safe, well-tested, and ready for PyPI.

---

## 📖 Reference Documentation

The Porkbun API documentation has been saved locally to avoid repeated web fetches:

- **File:** `porkbun_api_documentation.html`
- **Source:** https://porkbun.com/api/json/v3/documentation
- **Contents:** Full API reference including DNS, domains, DNSSEC, SSL, and pricing endpoints

---

## 📋 Final Decisions

| Aspect           | Choice                                                                   |
| ---------------- | ------------------------------------------------------------------------ |
| **Scope**        | Full Porkbun API (DNS, domains, DNSSEC, SSL, pricing)                    |
| **Python**       | >=3.13                                                                   |
| **HTTP Client**  | httpx                                                                    |
| **Architecture** | Async-first (`AsyncPiglet`), sync wrappers (`Piglet`)                    |
| **API Style**    | Namespaced: `piglet.dns.create()`, `piglet.domains.nameservers()`        |
| **Records**      | Type-safe dataclasses with validation                                    |
| **Auth**         | Env vars (`PORKBUN_API_KEY`, `PORKBUN_SECRET_KEY`) + constructor override|
| **Errors**       | Custom exception hierarchy                                               |
| **Rate Limits**  | Auto-retry with exponential backoff (configurable)                       |
| **CLI**          | Typer-based, starts small                                                |
| **Testing**      | pytest + pytest-cov (branch coverage), fixtures/parameterization, ty, ruff, Codecov |
| **Docs**         | MkDocs + mkdocstrings → GitHub Pages                                     |
| **CI/CD**        | GitHub Actions (lint, typecheck, test, docs, PyPI publish)               |
| **Package**      | `pip install oinker` → `from oinker import Piglet, AsyncPiglet`          |

---

## 🎨 Whimsy Guidelines

The goal: **delightful branding that makes devs smile, without sacrificing discoverability or Pythonic conventions.**

### ✅ Safe Whimsy (Won't Confuse Anyone)

| Element              | Whimsy Level | Notes                            |
| -------------------- | ------------ | -------------------------------- |
| Package name         | 🐷           | `oinker` - already fun           |
| Client classes       | 🐷           | `Piglet`, `AsyncPiglet`          |
| Method names         | 😐 (serious) | `.dns.list()`, `.ping()` - standard |
| CLI success messages | 🐷🐷         | "Squeee!", "Gobbled up"          |
| CLI data output      | 😐 (serious) | Clean tables, no puns            |
| Error messages       | 🐷           | Playful but informative          |
| Docstrings           | 🐷 (light)   | Occasional pig references        |
| README               | 🐷🐷         | Fun tagline, logo, personality   |
| API param names      | 😐 (serious) | `content`, `ttl`, `domain` - standard |
| Version codenames    | 🐷           | "First Oink", "Curly Tail"       |

### ⚠️ Whimsy to Avoid (Would Confuse)

| Idea                                               | Why Not                                    |
| -------------------------------------------------- | ------------------------------------------ |
| `piglet.snort()` instead of `piglet.ping()`        | Undiscoverable - what does snort do?       |
| `piglet.trough.list()` instead of `piglet.dns.list()` | Cute but obscures purpose               |
| `MudRecord` instead of `ARecord`                   | Obscures purpose                           |
| `from oinker import oink` as main function         | Too vague                                  |
| Pig puns in record field names                     | Terrible for docs                          |

### CLI Personality Examples

```bash
$ oinker ping
🐷 Oink! Connected successfully.
   Your IP: 203.0.113.42

$ oinker dns create example.com A www 1.2.3.4
🐷 Squeee! Created record 123458

$ oinker dns delete example.com --id 123458
🐷 Gobbled up record 123458

$ oinker --help
🐷 Oinker - Porkbun DNS management that doesn't stink!
```

### Error Message Personality

```python
class AuthenticationError(OinkerError):
    """Invalid API credentials."""
    # "🐷 Oops! Couldn't authenticate. Check your API keys aren't hogwash."

class RateLimitError(OinkerError):
    """Rate limit exceeded."""
    # "🐷 Whoa there! Slow your trot. Try again in {retry_after}s."

class NotFoundError(OinkerError):
    """Domain or record not found."""
    # "🐷 Couldn't find that in the pen. Double-check the domain/record ID."
```

### Version Codenames

```markdown
## 0.3.0 - "Snout Upgrade" (2026-03-15)
## 0.2.0 - "Curly Tail" (2026-02-01)
## 0.1.0 - "First Oink" (2026-01-20)
```

---

## 📁 Project Structure

```
oinker/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint, typecheck, test on PR/push
│       ├── docs.yml            # Build & deploy docs to GitHub Pages
│       └── publish.yml         # Publish to PyPI on release
├── docs/
│   ├── index.md                # Landing page
│   ├── getting-started.md      # Quick start guide
│   ├── async-vs-sync.md        # When to use which
│   ├── api/                    # Auto-generated from docstrings
│   └── cli.md                  # CLI reference
├── src/
│   └── oinker/
│       ├── __init__.py         # Public API exports
│       ├── _client.py          # AsyncPiglet (core async client)
│       ├── _sync.py            # Piglet (sync wrapper)
│       ├── _config.py          # Configuration & auth handling
│       ├── _http.py            # httpx wrapper, retry logic
│       ├── _exceptions.py      # Custom exception hierarchy
│       ├── _types.py           # Shared type definitions
│       ├── dns/
│       │   ├── __init__.py
│       │   ├── _api.py         # DNS operations (async)
│       │   ├── _records.py     # ARecord, MXRecord, etc.
│       │   └── _sync.py        # DNS sync wrapper
│       ├── domains/
│       │   ├── __init__.py
│       │   ├── _api.py         # Domain operations (async)
│       │   └── _sync.py        # Domain sync wrapper
│       ├── dnssec/
│       │   ├── __init__.py
│       │   ├── _api.py         # DNSSEC operations (async)
│       │   └── _sync.py        # DNSSEC sync wrapper
│       ├── ssl/
│       │   ├── __init__.py
│       │   ├── _api.py         # SSL operations (async)
│       │   └── _sync.py        # SSL sync wrapper
│       ├── pricing/
│       │   ├── __init__.py
│       │   └── _api.py         # Pricing (no auth needed)
│       └── cli/
│           ├── __init__.py
│           └── _main.py        # Typer CLI
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── test_client.py          # Client initialization tests
│   ├── test_config.py          # Config/auth tests
│   ├── test_exceptions.py      # Error handling tests
│   ├── test_http.py            # HTTP layer, retry logic
│   ├── dns/
│   │   ├── test_api.py         # DNS operations
│   │   └── test_records.py     # Record validation
│   ├── domains/
│   │   └── test_api.py
│   ├── dnssec/
│   │   └── test_api.py
│   ├── ssl/
│   │   └── test_api.py
│   ├── pricing/
│   │   └── test_api.py
│   └── cli/
│       └── test_main.py        # CLI tests
├── pyproject.toml              # Project config (uv, ruff, pytest, ty)
├── README.md                   # Project overview + quick examples
├── LICENSE                     # MIT
├── CHANGELOG.md                # Version history
├── PROJECT_PLAN.md             # This file
├── mkdocs.yml                  # Docs configuration
├── .gitignore                  # Python-friendly ignores (venv, __pycache__, .coverage, etc.)
└── renovate.json               # Automated dependency updates
```

---

## 🎯 Public API Surface

### Client Classes

```python
from oinker import Piglet, AsyncPiglet

# Sync (for scripts, CLI, simple use)
piglet = Piglet()
piglet = Piglet(api_key="...", secret_key="...")  # Override env vars

# Async (preferred for performance, async codebases)
async with AsyncPiglet() as piglet:
    ...
```

### DNS Operations

```python
from oinker import AsyncPiglet, ARecord, AAAARecord, MXRecord, TXTRecord, CNAMERecord

async with AsyncPiglet() as piglet:
    # List all records
    records = await piglet.dns.list("example.com")
    
    # Get specific record by ID
    record = await piglet.dns.get("example.com", record_id="123456")
    
    # Get by subdomain and type
    records = await piglet.dns.get_by_name_type("example.com", "A", subdomain="www")
    
    # Create records (type-safe!)
    record_id = await piglet.dns.create("example.com", ARecord(
        content="1.2.3.4",
        name="www",       # subdomain (optional)
        ttl=600,          # optional, default 600
    ))
    
    # Edit by ID
    await piglet.dns.edit("example.com", record_id="123456", ARecord(
        content="5.6.7.8",
        name="www",
    ))
    
    # Edit by subdomain/type (updates ALL matching)
    await piglet.dns.edit_by_name_type("example.com", "A", "www", content="5.6.7.8")
    
    # Delete by ID
    await piglet.dns.delete("example.com", record_id="123456")
    
    # Delete by subdomain/type
    await piglet.dns.delete_by_name_type("example.com", "A", "www")
```

### Domain Operations

```python
async with AsyncPiglet() as piglet:
    # List all domains
    domains = await piglet.domains.list()
    
    # Nameservers
    ns = await piglet.domains.get_nameservers("example.com")
    await piglet.domains.update_nameservers("example.com", [
        "ns1.example.com",
        "ns2.example.com",
    ])
    
    # URL forwarding
    forwards = await piglet.domains.get_url_forwards("example.com")
    await piglet.domains.add_url_forward("example.com", URLForward(
        location="https://porkbun.com",
        type="temporary",
        subdomain="blog",
    ))
    await piglet.domains.delete_url_forward("example.com", forward_id="123")
    
    # Domain availability
    availability = await piglet.domains.check("example.com")
    
    # Glue records
    glue = await piglet.domains.get_glue_records("example.com")
    await piglet.domains.create_glue_record("example.com", "ns1", ips=["1.2.3.4"])
```

### DNSSEC Operations

```python
async with AsyncPiglet() as piglet:
    records = await piglet.dnssec.list("example.com")
    await piglet.dnssec.create("example.com", DNSSECRecord(
        key_tag="64087",
        algorithm="13",
        digest_type="2",
        digest="15E445BD...",
    ))
    await piglet.dnssec.delete("example.com", key_tag="64087")
```

### SSL Operations

```python
async with AsyncPiglet() as piglet:
    bundle = await piglet.ssl.retrieve("example.com")
    # bundle.certificate_chain, bundle.private_key, bundle.public_key
```

### Pricing (No Auth Required)

```python
from oinker import get_pricing

pricing = await get_pricing()  # or sync: get_pricing_sync()
# pricing["com"].registration, pricing["com"].renewal, etc.
```

### Utility

```python
async with AsyncPiglet() as piglet:
    pong = await piglet.ping()  # Tests auth, returns your IP
```

---

## 🧱 DNS Record Types

```python
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address

@dataclass
class ARecord:
    content: IPv4Address | str  # Validated on init
    name: str | None = None     # Subdomain (None = root)
    ttl: int = 600
    notes: str | None = None

@dataclass
class AAAARecord:
    content: IPv6Address | str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

@dataclass
class MXRecord:
    content: str                # Mail server hostname
    priority: int               # Required for MX
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

@dataclass
class TXTRecord:
    content: str
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

@dataclass
class CNAMERecord:
    content: str                # Target hostname
    name: str | None = None
    ttl: int = 600
    notes: str | None = None

# Also: NSRecord, SRVRecord, TLSARecord, CAARecord, 
#       HTTPSRecord, SVCBRecord, SSHFPRecord, ALIASRecord
```

---

## ⚠️ Exception Hierarchy

```python
class OinkerError(Exception):
    """Base exception for all oinker errors."""

class AuthenticationError(OinkerError):
    """Invalid or missing API credentials."""

class AuthorizationError(OinkerError):
    """Valid creds but not authorized for this domain/action."""

class RateLimitError(OinkerError):
    """Rate limit exceeded. Has retry_after attribute."""
    retry_after: float

class NotFoundError(OinkerError):
    """Domain or record not found."""

class ValidationError(OinkerError):
    """Invalid record data (e.g., bad IP format)."""

class APIError(OinkerError):
    """Generic API error. Has status_code and message."""
    status_code: int
    message: str
```

---

## 🧪 Testing Strategy

### Principles

- **Fixtures over helpers** - Reusable test components via pytest fixtures
- **Parameterization** - Test multiple cases without code duplication
- **Mocks with specs** - `AsyncMock(spec=SomeClass)` catches attribute errors
- **Focus on critical paths** - Don't chase 100% coverage blindly
- **Docstrings required** - All public functions and classes must have docstrings (target: 80%+ coverage)

### Example Fixtures (`conftest.py`)

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def api_credentials():
    return {"api_key": "test_key", "secret_key": "test_secret"}

@pytest.fixture
def mock_http_client():
    return AsyncMock(spec=httpx.AsyncClient)

@pytest.fixture
async def async_piglet(api_credentials, mock_http_client):
    async with AsyncPiglet(**api_credentials, _http_client=mock_http_client) as p:
        yield p

@pytest.fixture
def sample_dns_response():
    return {
        "status": "SUCCESS",
        "records": [
            {"id": "123", "name": "example.com", "type": "A", "content": "1.2.3.4", "ttl": "600", "prio": "0"}
        ]
    }
```

### Example Parameterized Tests

```python
import pytest
from contextlib import nullcontext
from oinker.dns import ARecord, AAAARecord, MXRecord

@pytest.mark.parametrize("record_class,content,expected_valid", [
    (ARecord, "1.2.3.4", True),
    (ARecord, "999.999.999.999", False),
    (ARecord, "not-an-ip", False),
    (AAAARecord, "2001:db8::1", True),
    (AAAARecord, "1.2.3.4", False),
])
def test_record_validation(record_class, content, expected_valid):
    expectation = nullcontext() if expected_valid else pytest.raises(ValidationError)
    with expectation:
        record_class(content=content)

@pytest.mark.parametrize("status_code,expected_exception", [
    (401, AuthenticationError),
    (403, AuthorizationError),
    (404, NotFoundError),
    (429, RateLimitError),
    (500, APIError),
])
async def test_error_handling(async_piglet, mock_http_client, status_code, expected_exception):
    mock_http_client.post.return_value = httpx.Response(status_code, json={"status": "ERROR"})
    with pytest.raises(expected_exception):
        await async_piglet.dns.list("example.com")
```

---

## 🖥️ CLI Design (Starting Small)

```bash
# Authentication (uses env vars by default)
$ export PORKBUN_API_KEY="pk1_..."
$ export PORKBUN_SECRET_KEY="sk1_..."

# Test connection
$ oinker ping
🐷 Oink! Connected successfully.
   Your IP: 203.0.113.42

# DNS commands
$ oinker dns list example.com
┌────────┬─────────────────┬──────┬───────────┬─────┐
│ ID     │ Name            │ Type │ Content   │ TTL │
├────────┼─────────────────┼──────┼───────────┼─────┤
│ 123456 │ example.com     │ A    │ 1.2.3.4   │ 600 │
│ 123457 │ www.example.com │ A    │ 1.2.3.4   │ 600 │
└────────┴─────────────────┴──────┴───────────┴─────┘

$ oinker dns create example.com A www 1.2.3.4
🐷 Squeee! Created record 123458

$ oinker dns delete example.com --id 123458
🐷 Gobbled up record 123458

# Domain commands
$ oinker domains list
$ oinker domains nameservers example.com
```

---

## 📦 Dependencies

### Runtime

```toml
[project]
dependencies = [
    "httpx>=0.28",
]

[project.optional-dependencies]
cli = ["typer>=0.15", "rich>=13"]
```

### Development

```toml
[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "pytest-asyncio>=0.25",
    "respx>=0.22",           # Mock httpx
    "ty>=0.1",               # Type checker
    "ruff>=0.9",
    "mkdocs>=1.6",
    "mkdocs-material>=9",
    "mkdocstrings[python]>=0.27",
]
```

---

## 🔧 Tool Configuration (`pyproject.toml`)

```toml
[project]
name = "oinker"
version = "0.1.0"
description = "A delightfully Pythonic library for managing DNS at Porkbun 🐷"
readme = "README.md"
license = "MIT"
authors = [{ name = "Major Hayden", email = "major@mhtx.net" }]
requires-python = ">=3.13"
keywords = ["dns", "porkbun", "api", "domains"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Internet :: Name Service (DNS)",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/major/oinker"
Documentation = "https://major.github.io/oinker"
Repository = "https://github.com/major/oinker"

[project.scripts]
oinker = "oinker.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "ASYNC"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
addopts = "--cov=oinker --cov-report=term-missing"

[tool.coverage.run]
source = ["src/oinker"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]

[tool.ty]
python_version = "3.13"
```

---

## 🔄 Renovate Configuration (`renovate.json`)

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    ":separateMajorReleases",
    ":combinePatchMinorReleases",
    ":enableVulnerabilityAlertsWithLabel('security')",
    ":semanticCommits",
    ":automergeMinor",
    ":automergeDigest",
    "group:allNonMajor"
  ],
  "labels": ["dependencies"],
  "packageRules": [
    {
      "description": "Group all dev dependency updates",
      "matchDepTypes": ["devDependencies"],
      "groupName": "dev dependencies"
    },
    {
      "description": "Automerge non-major updates for trusted packages",
      "matchPackageNames": ["ruff", "pytest", "pytest-cov", "pytest-asyncio", "mkdocs*", "ty"],
      "automerge": true
    },
    {
      "description": "Require approval for major updates",
      "matchUpdateTypes": ["major"],
      "automerge": false
    }
  ],
  "pip_requirements": {
    "fileMatch": ["requirements.*\\.txt$"]
  },
  "pep621": {
    "fileMatch": ["pyproject\\.toml$"]
  },
  "schedule": ["before 6am on monday"]
}
```

---

## 🚀 GitHub Actions

### CI (`ci.yml`)

```yaml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run ty check

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.13", "3.14"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --dev
      - run: uv run pytest --cov-report=xml
      - uses: codecov/codecov-action@v4
```

### Docs (`docs.yml`)

```yaml
name: Docs
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run mkdocs gh-deploy --force
```

### Publish (`publish.yml`)

```yaml
name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write  # Trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

---

## 📚 Documentation Structure

```yaml
# mkdocs.yml
site_name: Oinker 🐷
site_description: A delightfully Pythonic library for managing DNS at Porkbun
repo_url: https://github.com/major/oinker
theme:
  name: material
  palette:
    primary: pink
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            docstring_style: google
nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Async vs Sync: async-vs-sync.md
  - CLI Reference: cli.md
  - API Reference:
      - Client: api/client.md
      - DNS: api/dns.md
      - Domains: api/domains.md
      - DNSSEC: api/dnssec.md
      - SSL: api/ssl.md
      - Exceptions: api/exceptions.md
```

---

## 📅 Implementation Phases

### Phase 1: Foundation 🏗️

- [ ] Project structure setup
- [ ] Python-friendly `.gitignore`
- [ ] `renovate.json` for automated dependency updates
- [ ] pyproject.toml with all tooling
- [ ] Config & auth handling (`_config.py`)
- [ ] HTTP layer with retry logic (`_http.py`)
- [ ] Exception hierarchy (`_exceptions.py`)
- [ ] Basic `AsyncPiglet` and `Piglet` scaffolding
- [ ] GitHub Actions CI workflow

### Phase 2: DNS Operations 🌐

- [ ] DNS record dataclasses with validation
- [ ] `piglet.dns.*` async implementation
- [ ] Sync wrappers
- [ ] Comprehensive tests (fixtures, parameterization)

### Phase 3: Domain Operations 📁

- [ ] Nameservers, URL forwarding, glue records
- [ ] Domain listing and availability check
- [ ] Tests

### Phase 4: DNSSEC & SSL 🔐

- [ ] DNSSEC CRUD
- [ ] SSL bundle retrieval
- [ ] Tests

### Phase 5: CLI 🖥️

- [ ] Typer app setup
- [ ] `ping`, `dns list/create/delete`
- [ ] Rich table output
- [ ] Tests

### Phase 6: Polish & Publish 🚀

- [ ] MkDocs setup
- [ ] README with examples
- [ ] GitHub Actions docs deployment
- [ ] PyPI trusted publishing setup
- [ ] First release: "First Oink" 🎉

---

## 🐷 Ready to Build!

*Oink oink!* 🚀
