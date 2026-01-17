# 🐷 Oinker

**A delightfully Pythonic library for managing domains at Porkbun.** 🐽

Oinker provides a modern, type-safe Python interface to the [Porkbun API](https://porkbun.com/api/json/v3/documentation). DNS records, DNSSEC, SSL certificates, URL forwarding, and more. Async-first for performance, with sync wrappers for simplicity.

## ✨ Features

- **Complete API coverage** - DNS, DNSSEC, SSL, domains, URL forwarding, glue records
- **Async-first design** - Built on httpx for modern async/await support
- **Type-safe records** - Dataclasses with validation for all DNS record types
- **Sync wrappers** - Use `Piglet` when you don't need async
- **CLI included** - Manage domains from the command line
- **Auto-retry** - Exponential backoff for transient failures
- **Python 3.13+** - Modern Python with full type annotations

## 🚀 Quick Example

=== "Async (recommended)"

    ```python
    from oinker import AsyncPiglet, ARecord

    async with AsyncPiglet() as piglet:
        # Test connection
        pong = await piglet.ping()
        print(f"Your IP: {pong.your_ip}")

        # Create an A record
        record_id = await piglet.dns.create(
            "example.com",
            ARecord(content="1.2.3.4", name="www")
        )
        print(f"Created record: {record_id}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ARecord

    with Piglet() as piglet:
        pong = piglet.ping()
        print(f"Your IP: {pong.your_ip}")

        record_id = piglet.dns.create(
            "example.com",
            ARecord(content="1.2.3.4", name="www")
        )
    ```

=== "CLI"

    ```bash
    # Test connection
    oinker ping

    # List DNS records
    oinker dns list example.com

    # Create an A record
    oinker dns create example.com A www 1.2.3.4
    ```

## 📦 Installation

```bash
pip install oinker
```

For CLI support:

```bash
pip install "oinker[cli]"
```

## 🔑 Authentication

Set your Porkbun API credentials as environment variables:

```bash
export PORKBUN_API_KEY="pk1_..."
export PORKBUN_SECRET_KEY="sk1_..."
```

Or pass them directly:

```python
from oinker import AsyncPiglet

async with AsyncPiglet(api_key="pk1_...", secret_key="sk1_...") as piglet:
    ...
```

## 📚 What's Next?

- [Getting Started](getting-started.md) - Installation and first steps
- [Async vs Sync](async-vs-sync.md) - When to use which client
- [CLI Reference](cli.md) - Command-line usage
- [API Reference](api/client.md) - Full API documentation
