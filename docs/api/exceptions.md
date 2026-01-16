# Exceptions

All Oinker exceptions inherit from `OinkerError` for easy catching.

```python
from oinker import OinkerError

try:
    await piglet.dns.list("example.com")
except OinkerError as e:
    print(f"Something went wrong: {e}")
```

## Exception Hierarchy

```text
OinkerError
├── AuthenticationError
├── AuthorizationError
├── RateLimitError
├── NotFoundError
├── ValidationError
└── APIError
```

## Exceptions

### OinkerError

::: oinker.OinkerError

### AuthenticationError

::: oinker.AuthenticationError

### AuthorizationError

::: oinker.AuthorizationError

### RateLimitError

::: oinker.RateLimitError

### NotFoundError

::: oinker.NotFoundError

### ValidationError

::: oinker.ValidationError

### APIError

::: oinker.APIError
