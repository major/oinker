# oinker

A delightfully Pythonic library for managing DNS at Porkbun.

## Installation

```bash
pip install oinker
```

## Quick Start

```python
from oinker import Piglet

with Piglet(api_key="pk1_...", secret_key="sk1_...") as client:
    response = client.ping()
    print(f"Connected from {response.your_ip}")
```

### Async Usage

```python
from oinker import AsyncPiglet

async with AsyncPiglet(api_key="pk1_...", secret_key="sk1_...") as client:
    response = await client.ping()
    print(f"Connected from {response.your_ip}")
```

## License

MIT
