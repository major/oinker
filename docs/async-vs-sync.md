# Async vs Sync

Oinker provides two client classes: `AsyncPiglet` (async) and `Piglet` (sync). This guide helps you choose the right one.

## Quick Decision

| Use Case | Recommended |
|----------|-------------|
| Web frameworks (FastAPI, Starlette) | `AsyncPiglet` |
| Scripts and CLI tools | `Piglet` |
| Background tasks in async apps | `AsyncPiglet` |
| Jupyter notebooks | `Piglet` |
| High-throughput batch operations | `AsyncPiglet` |
| Simple automation scripts | `Piglet` |

## AsyncPiglet (Async)

The async client is the **primary implementation**. It's built on httpx and provides full async/await support.

```python
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    response = await piglet.ping()
```

### When to Use

- **Async web frameworks**: FastAPI, Starlette, Quart, etc.
- **Concurrent operations**: When you need to make multiple API calls in parallel
- **Long-running services**: Better resource utilization
- **Performance-critical code**: Non-blocking I/O

### Concurrent Operations

The async client shines when you need to perform multiple operations:

```python
import asyncio
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    # Fetch records from multiple domains concurrently
    domains = ["example.com", "example.org", "example.net"]
    tasks = [piglet.dns.list(domain) for domain in domains]
    results = await asyncio.gather(*tasks)

    for domain, records in zip(domains, results):
        print(f"{domain}: {len(records)} records")
```

### FastAPI Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from oinker import AsyncPiglet

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.piglet = AsyncPiglet()
    try:
        await app.state.piglet.__aenter__()
        yield
    finally:
        await app.state.piglet.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)

def get_piglet(request) -> AsyncPiglet:
    return request.app.state.piglet

@app.get("/dns/{domain}")
async def list_records(domain: str, piglet: AsyncPiglet = Depends(get_piglet)):
    return await piglet.dns.list(domain)
```

## Piglet (Sync)

The sync client wraps `AsyncPiglet` for use in synchronous code. It manages its own event loop internally.

```python
from oinker import Piglet

with Piglet() as piglet:
    response = piglet.ping()
```

### When to Use

- **Scripts**: One-off automation scripts
- **CLI tools**: Command-line utilities
- **Jupyter notebooks**: Interactive exploration
- **Legacy codebases**: When async isn't an option
- **Simple use cases**: When you don't need concurrency

### Manual Lifecycle Management

If you're not using a context manager:

```python
from oinker import Piglet

piglet = Piglet()
try:
    response = piglet.ping()
finally:
    piglet.close()
```

## API Parity

Both clients have identical APIs. The only difference is `async`/`await`:

=== "Async"

    ```python
    async with AsyncPiglet() as piglet:
        records = await piglet.dns.list("example.com")
        record_id = await piglet.dns.create("example.com", ARecord(...))
        await piglet.dns.delete("example.com", record_id=record_id)
    ```

=== "Sync"

    ```python
    with Piglet() as piglet:
        records = piglet.dns.list("example.com")
        record_id = piglet.dns.create("example.com", ARecord(...))
        piglet.dns.delete("example.com", record_id=record_id)
    ```

## Performance Comparison

For single operations, both clients perform similarly. The async client's advantage appears with concurrent operations:

| Scenario | Sync | Async |
|----------|------|-------|
| Single DNS lookup | ~100ms | ~100ms |
| 10 sequential lookups | ~1000ms | ~1000ms |
| 10 concurrent lookups | ~1000ms | ~200ms |

## Common Pitfalls

### Don't Mix Async and Sync

Avoid using the sync client inside async code:

```python
# BAD: Blocks the event loop
async def bad_example():
    piglet = Piglet()  # Don't do this in async code
    return piglet.ping()

# GOOD: Use AsyncPiglet in async code
async def good_example():
    async with AsyncPiglet() as piglet:
        return await piglet.ping()
```

### Event Loop Management

The sync client creates its own event loop. Don't use it if you're already running an async event loop:

```python
import asyncio

async def main():
    # BAD: Piglet will conflict with the running loop
    # piglet = Piglet()

    # GOOD: Use AsyncPiglet
    async with AsyncPiglet() as piglet:
        await piglet.ping()

asyncio.run(main())
```
