# Examples

Welcome to the Oinker examples! This section provides practical, copy-paste-ready code for every Porkbun API operation.

## Quick Navigation

| Section | What You'll Learn |
|---------|-------------------|
| [DNS Records](dns.md) | Create, list, update, and delete DNS records of all types |
| [Domains](domains.md) | Manage nameservers, URL forwarding, glue records, and check availability |
| [DNSSEC](dnssec.md) | Configure DNSSEC at the registry level |
| [SSL Certificates](ssl.md) | Retrieve free SSL certificates for your domains |
| [Pricing](pricing.md) | Query TLD pricing (no authentication required) |
| [Dynamic DNS](dynamic-dns.md) | Build a complete dynamic DNS updater script |

## Before You Start

### Installation

```bash
pip install oinker
```

### Authentication

Set your Porkbun API credentials:

```bash
export PORKBUN_API_KEY="pk1_..."
export PORKBUN_SECRET_KEY="sk1_..."
```

!!! tip "Getting API Keys"
    1. Log in to [Porkbun](https://porkbun.com/)
    2. Go to **Account** > **API Access**
    3. Create an API key pair
    4. Enable API access for each domain you want to manage

### Async vs Sync

All examples show both async and sync versions. Use async for web applications and concurrent operations; use sync for scripts and CLI tools.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        result = await piglet.ping()
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        result = piglet.ping()
    ```

## Example Structure

Each example page follows this pattern:

1. **Quick Start** - The most common operation
2. **All Operations** - Every API method with examples
3. **Real-World Patterns** - Practical use cases combining multiple operations

Ready to dive in? Start with [DNS Records](dns.md) - the most commonly used API.
