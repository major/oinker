# 🔐 DNSSEC

DNSSEC (DNS Security Extensions) management operations and types.

## 🚀 Quick Examples

### List DNSSEC Records

```python
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    records = await piglet.dnssec.list("example.com")
    for record in records:
        print(f"Key Tag: {record.key_tag}")
        print(f"Algorithm: {record.algorithm}")
        print(f"Digest Type: {record.digest_type}")
        print(f"Digest: {record.digest[:32]}...")
```

### Create DNSSEC Record

```python
from oinker import AsyncPiglet, DNSSECRecordCreate

async with AsyncPiglet() as piglet:
    await piglet.dnssec.create(
        "example.com",
        DNSSECRecordCreate(
            key_tag="64087",
            algorithm="13",
            digest_type="2",
            digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
        )
    )
```

### Delete DNSSEC Record

```python
async with AsyncPiglet() as piglet:
    # Delete by key tag
    await piglet.dnssec.delete("example.com", key_tag="64087")
```

!!! note "Registry Behavior"
    Most registries will delete all DNSSEC records with matching data, not just
    the record with the matching key tag.

## Operations

### AsyncDNSSECAPI

::: oinker.dnssec.AsyncDNSSECAPI
    options:
      members:
        - list
        - create
        - delete

### SyncDNSSECAPI

::: oinker.dnssec.SyncDNSSECAPI
    options:
      members:
        - list
        - create
        - delete

## Types

### DNSSECRecord

::: oinker.DNSSECRecord

### DNSSECRecordCreate

::: oinker.DNSSECRecordCreate
