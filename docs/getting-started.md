# 🐷 Getting Started

This guide will walk you through installing Oinker and making your first API calls.

## 📦 Installation

Install Oinker using pip:

```bash
pip install oinker
```

For CLI support, install the optional dependencies:

```bash
pip install "oinker[cli]"
```

### Using uv

If you're using [uv](https://docs.astral.sh/uv/):

```bash
uv add oinker
# Or with CLI support
uv add "oinker[cli]"
```

## 🔑 Getting API Credentials

1. Log in to your [Porkbun account](https://porkbun.com/)
2. Go to **Account** → **API Access**
3. Create an API key pair
4. Enable API access for each domain you want to manage

!!! warning "Domain API Access"
    You must explicitly enable API access for each domain in your Porkbun dashboard.
    Go to the domain's management page and toggle "API Access" to enabled.

## ⚙️ Configuration

### Environment Variables (Recommended)

Set your credentials as environment variables:

```bash
export PORKBUN_API_KEY="pk1_..."
export PORKBUN_SECRET_KEY="sk1_..."
```

The client will automatically use these when no credentials are passed explicitly.

### Direct Configuration

You can also pass credentials directly:

```python
from oinker import AsyncPiglet

async with AsyncPiglet(
    api_key="pk1_...",
    secret_key="sk1_..."
) as piglet:
    ...
```

## 🚀 Your First Request

Let's verify your credentials work by calling the ping endpoint:

=== "Async"

    ```python
    import asyncio
    from oinker import AsyncPiglet

    async def main():
        async with AsyncPiglet() as piglet:
            response = await piglet.ping()
            print(f"Connected! Your IP: {response.your_ip}")

    asyncio.run(main())
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        response = piglet.ping()
        print(f"Connected! Your IP: {response.your_ip}")
    ```

=== "CLI"

    ```bash
    oinker ping
    ```

## 📝 Working with DNS Records

### List Records

```python
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    records = await piglet.dns.list("example.com")
    for record in records:
        print(f"{record.record_type} {record.name} -> {record.content}")
```

### Create Records

Oinker provides type-safe dataclasses for each record type:

```python
from oinker import AsyncPiglet, ARecord, MXRecord, TXTRecord

async with AsyncPiglet() as piglet:
    # A record
    await piglet.dns.create(
        "example.com",
        ARecord(content="1.2.3.4", name="www")
    )

    # MX record with priority
    await piglet.dns.create(
        "example.com",
        MXRecord(content="mail.example.com", priority=10)
    )

    # TXT record
    await piglet.dns.create(
        "example.com",
        TXTRecord(content="v=spf1 include:_spf.example.com ~all")
    )
```

### Edit Records

```python
# Edit by ID
await piglet.dns.edit(
    "example.com",
    record_id="123456",
    record=ARecord(content="5.6.7.8", name="www")
)

# Edit by name and type
await piglet.dns.edit_by_name_type(
    "example.com",
    record_type="A",
    subdomain="www",
    content="5.6.7.8"
)
```

### Delete Records

```python
# Delete by ID
await piglet.dns.delete("example.com", record_id="123456")

# Delete by name and type
await piglet.dns.delete_by_name_type(
    "example.com",
    record_type="A",
    subdomain="www"
)
```

## ⚠️ Error Handling

Oinker raises specific exceptions for different error types:

```python
from oinker import (
    AsyncPiglet,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    OinkerError,
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
    except ValidationError as e:
        print(f"Invalid data: {e}")
    except OinkerError as e:
        print(f"API error: {e}")
```

## 📚 Next Steps

- [Async vs Sync](async-vs-sync.md) - Learn when to use each client
- [CLI Reference](cli.md) - Manage DNS from the command line
- [API Reference](api/client.md) - Full API documentation
