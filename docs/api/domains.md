# 🌐 Domains

Domain management operations and types.

## 🚀 Quick Examples

### List All Domains

```python
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    # List all domains in account
    domains = await piglet.domains.list()
    for domain in domains:
        print(f"{domain.domain} - expires {domain.expire_date}")

    # Include label information
    domains = await piglet.domains.list(include_labels=True)
    for domain in domains:
        if domain.labels:
            labels = ", ".join(label.title for label in domain.labels)
            print(f"{domain.domain} [{labels}]")
```

### Nameservers

```python
async with AsyncPiglet() as piglet:
    # Get current nameservers
    nameservers = await piglet.domains.get_nameservers("example.com")
    print(f"Current nameservers: {nameservers}")

    # Update nameservers
    await piglet.domains.update_nameservers("example.com", [
        "ns1.example.com",
        "ns2.example.com",
    ])
```

### URL Forwarding

```python
from oinker import URLForwardCreate

async with AsyncPiglet() as piglet:
    # Get existing forwards
    forwards = await piglet.domains.get_url_forwards("example.com")
    for forward in forwards:
        print(f"{forward.subdomain or '@'} -> {forward.location}")

    # Add a new forward
    await piglet.domains.add_url_forward(
        "example.com",
        URLForwardCreate(
            subdomain="blog",
            location="https://blog.example.com",
            forward_type="permanent",
            include_path=True,
            wildcard=False,
        )
    )

    # Delete a forward by ID
    await piglet.domains.delete_url_forward("example.com", forward_id="12345")
```

### Check Domain Availability

```python
async with AsyncPiglet() as piglet:
    availability = await piglet.domains.check("coolname.com")
    if availability.available:
        print(f"Available! Price: ${availability.pricing.registration}")
    else:
        print("Domain is taken")
```

### Glue Records

Glue records are used when you run your own nameservers on subdomains of your domain.

```python
async with AsyncPiglet() as piglet:
    # Get existing glue records
    glue_records = await piglet.domains.get_glue_records("example.com")
    for record in glue_records:
        print(f"{record.host}: IPv4={record.ipv4}, IPv6={record.ipv6}")

    # Create a glue record for ns1.example.com
    await piglet.domains.create_glue_record(
        "example.com",
        subdomain="ns1",
        ips=["192.168.1.1", "2001:db8::1"]
    )

    # Update a glue record
    await piglet.domains.update_glue_record(
        "example.com",
        subdomain="ns1",
        ips=["192.168.1.2", "2001:db8::2"]
    )

    # Delete a glue record
    await piglet.domains.delete_glue_record("example.com", subdomain="ns1")
```

## Operations

### AsyncDomainsAPI

::: oinker.domains.AsyncDomainsAPI
    options:
      members:
        - list
        - get_nameservers
        - update_nameservers
        - get_url_forwards
        - add_url_forward
        - delete_url_forward
        - check
        - get_glue_records
        - create_glue_record
        - update_glue_record
        - delete_glue_record

### SyncDomainsAPI

::: oinker.domains.SyncDomainsAPI
    options:
      members:
        - list
        - get_nameservers
        - update_nameservers
        - get_url_forwards
        - add_url_forward
        - delete_url_forward
        - check
        - get_glue_records
        - create_glue_record
        - update_glue_record
        - delete_glue_record

## Types

### DomainInfo

::: oinker.DomainInfo

### DomainLabel

::: oinker.DomainLabel

### DomainAvailability

::: oinker.DomainAvailability

### DomainPricing

::: oinker.DomainPricing

### URLForward

::: oinker.URLForward

### URLForwardCreate

::: oinker.URLForwardCreate

### GlueRecord

::: oinker.GlueRecord
