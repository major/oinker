# 🐷 Oinker

> *Domain management that doesn't stink!* 🐽

A delightfully Pythonic library for managing domains at [Porkbun](https://porkbun.com). DNS records, DNSSEC, SSL certificates, URL forwarding, and more. Async-first with sync wrappers, type-safe, and thoroughly tested.

**[📚 Full Documentation](https://major.github.io/oinker/)** | **[🐽 Not affiliated with Porkbun](#-disclaimer)**

[![CI](https://github.com/major/oinker/actions/workflows/ci.yml/badge.svg)](https://github.com/major/oinker/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/major/oinker/branch/main/graph/badge.svg)](https://codecov.io/gh/major/oinker)
[![PyPI version](https://badge.fury.io/py/oinker.svg)](https://pypi.org/project/oinker/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🚀 **Async-first design** - Built on httpx for modern async/await support
- 🔒 **Type-safe records** - Dataclasses with validation for all DNS record types
- 🔄 **Sync wrappers** - Use `Piglet` when you don't need async
- 💻 **CLI included** - Manage DNS from the command line
- 🔁 **Auto-retry** - Exponential backoff for transient failures
- 🐍 **Python 3.13+** - Modern Python with full type annotations

## 📦 Installation

```bash
pip install oinker
```

For CLI support:

```bash
pip install "oinker[cli]"
```

## 🚀 Quick Start

Set your Porkbun API credentials:

```bash
export PORKBUN_API_KEY="pk1_..."
export PORKBUN_SECRET_KEY="sk1_..."
```

### Async (Recommended)

```python
from oinker import AsyncPiglet, ARecord

async with AsyncPiglet() as piglet:
    # Test connection
    pong = await piglet.ping()
    print(f"Your IP: {pong.your_ip}")

    # List DNS records
    records = await piglet.dns.list("example.com")
    for record in records:
        print(f"{record.record_type} {record.name} -> {record.content}")

    # Create an A record
    record_id = await piglet.dns.create(
        "example.com",
        ARecord(content="1.2.3.4", name="www")
    )

    # Delete by ID
    await piglet.dns.delete("example.com", record_id=record_id)
```

### Sync

```python
from oinker import Piglet, ARecord

with Piglet() as piglet:
    pong = piglet.ping()
    print(f"Your IP: {pong.your_ip}")

    records = piglet.dns.list("example.com")
```

### CLI

```bash
# Test connection
$ oinker ping
🐷 Oink! Connected successfully.
   Your IP: 203.0.113.42

# List DNS records
$ oinker dns list example.com
┌────────┬─────────────────┬──────┬───────────┬─────┐
│ ID     │ Name            │ Type │ Content   │ TTL │
├────────┼─────────────────┼──────┼───────────┼─────┤
│ 123456 │ example.com     │ A    │ 1.2.3.4   │ 600 │
│ 123457 │ www.example.com │ A    │ 1.2.3.4   │ 600 │
└────────┴─────────────────┴──────┴───────────┴─────┘

# Create an A record
$ oinker dns create example.com A www 1.2.3.4
🐷 Squeee! Created record 123458

# Delete a record
$ oinker dns delete example.com --id 123458
🐷 Gobbled up record 123458
```

## 📝 DNS Record Types

Oinker provides type-safe dataclasses for all Porkbun-supported record types:

```python
from oinker import (
    ARecord,      # IPv4 address
    AAAARecord,   # IPv6 address
    MXRecord,     # Mail server
    TXTRecord,    # Text record
    CNAMERecord,  # Canonical name
    ALIASRecord,  # ALIAS/ANAME
    NSRecord,     # Name server
    SRVRecord,    # Service record
    TLSARecord,   # DANE/TLSA
    CAARecord,    # CA Authorization
    HTTPSRecord,  # HTTPS binding
    SVCBRecord,   # Service binding
    SSHFPRecord,  # SSH fingerprint
)
```

Records validate their content on construction:

```python
from oinker import ARecord, ValidationError

try:
    ARecord(content="not-an-ip")
except ValidationError as e:
    print(e)  # Invalid IPv4 address: not-an-ip
```

## 🌐 Domain Operations

```python
async with AsyncPiglet() as piglet:
    # List all domains
    domains = await piglet.domains.list()

    # Get/update nameservers
    ns = await piglet.domains.get_nameservers("example.com")
    await piglet.domains.update_nameservers("example.com", [
        "ns1.example.com",
        "ns2.example.com",
    ])

    # URL forwarding
    forwards = await piglet.domains.get_url_forwards("example.com")

    # Check domain availability
    availability = await piglet.domains.check("example.com")
```

## 🔐 DNSSEC

```python
from oinker import DNSSECRecordCreate

async with AsyncPiglet() as piglet:
    # List DNSSEC records
    records = await piglet.dnssec.list("example.com")

    # Create DNSSEC record
    await piglet.dnssec.create("example.com", DNSSECRecordCreate(
        key_tag="64087",
        algorithm="13",
        digest_type="2",
        digest="15E445BD...",
    ))
```

## 🔒 SSL Certificates

```python
async with AsyncPiglet() as piglet:
    bundle = await piglet.ssl.retrieve("example.com")
    print(bundle.certificate_chain)
    print(bundle.private_key)
```

## ⚠️ Error Handling

```python
from oinker import (
    AsyncPiglet,
    OinkerError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

async with AsyncPiglet() as piglet:
    try:
        await piglet.dns.list("example.com")
    except AuthenticationError:
        print("Check your API credentials")
    except NotFoundError:
        print("Domain not found or API access not enabled")
    except RateLimitError as e:
        print(f"Slow down! Retry after {e.retry_after}s")
    except OinkerError as e:
        print(f"API error: {e}")
```

## 📚 Documentation

For more examples and detailed API reference, check out the **[full documentation](https://major.github.io/oinker/)**.

## 🐷 Disclaimer

This project is not affiliated with [Porkbun](https://porkbun.com) in any way. It's just a passion project by someone who really, really loves Porkbun. They're amazing! 🐽

## 📄 License

MIT
