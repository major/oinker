# 🔒 SSL

SSL certificate retrieval operations.

## 🚀 Quick Example

```python
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    bundle = await piglet.ssl.retrieve("example.com")

    # Save the certificate chain
    with open("cert.pem", "w") as f:
        f.write(bundle.certificate_chain)

    # Save the private key
    with open("key.pem", "w") as f:
        f.write(bundle.private_key)

    # Public key is also available
    print(bundle.public_key)
```

!!! note "Free SSL Certificates"
    Porkbun provides free SSL certificates for domains using their nameservers.
    The certificates are issued by Let's Encrypt and auto-renew.

## Operations

### AsyncSSLAPI

::: oinker.ssl.AsyncSSLAPI
    options:
      members:
        - retrieve

### SyncSSLAPI

::: oinker.ssl.SyncSSLAPI
    options:
      members:
        - retrieve

## Types

### SSLBundle

::: oinker.SSLBundle
