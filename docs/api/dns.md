# 📝 DNS

DNS record management operations and types.

## 🚀 Quick Examples

### List All Records

```python
from oinker import AsyncPiglet

async with AsyncPiglet() as piglet:
    records = await piglet.dns.list("example.com")
    for record in records:
        print(f"{record.record_type} {record.name} -> {record.content}")
```

### Get a Single Record by ID

```python
async with AsyncPiglet() as piglet:
    record = await piglet.dns.get("example.com", record_id="123456")
    print(f"{record.record_type} {record.name} -> {record.content}")
```

### Get Records by Name and Type

```python
async with AsyncPiglet() as piglet:
    # Get all A records for www subdomain
    records = await piglet.dns.get_by_name_type(
        "example.com",
        record_type="A",
        subdomain="www"
    )
    for record in records:
        print(f"{record.name} -> {record.content}")

    # Get root domain A records (no subdomain)
    root_records = await piglet.dns.get_by_name_type(
        "example.com",
        record_type="A"
    )
```

### Create Records

```python
from oinker import AsyncPiglet, ARecord, MXRecord, TXTRecord

async with AsyncPiglet() as piglet:
    # A record for www subdomain
    record_id = await piglet.dns.create(
        "example.com",
        ARecord(content="1.2.3.4", name="www")
    )
    print(f"Created record: {record_id}")

    # MX record with priority
    await piglet.dns.create(
        "example.com",
        MXRecord(content="mail.example.com", priority=10)
    )

    # TXT record for SPF
    await piglet.dns.create(
        "example.com",
        TXTRecord(content="v=spf1 include:_spf.example.com ~all")
    )
```

### Edit Records

```python
from oinker import ARecord

async with AsyncPiglet() as piglet:
    # Edit by record ID
    await piglet.dns.edit(
        "example.com",
        record_id="123456",
        record=ARecord(content="5.6.7.8", name="www")
    )

    # Edit all matching records by name and type
    await piglet.dns.edit_by_name_type(
        "example.com",
        record_type="A",
        subdomain="www",
        content="5.6.7.8"
    )
```

### Delete Records

```python
async with AsyncPiglet() as piglet:
    # Delete by record ID
    await piglet.dns.delete("example.com", record_id="123456")

    # Delete all matching records by name and type
    await piglet.dns.delete_by_name_type(
        "example.com",
        record_type="A",
        subdomain="www"
    )
```

## Operations

### AsyncDNSAPI

::: oinker.dns.AsyncDNSAPI
    options:
      members:
        - list
        - get
        - get_by_name_type
        - create
        - edit
        - edit_by_name_type
        - delete
        - delete_by_name_type

### SyncDNSAPI

::: oinker.dns.SyncDNSAPI
    options:
      members:
        - list
        - get
        - get_by_name_type
        - create
        - edit
        - edit_by_name_type
        - delete
        - delete_by_name_type

## Record Types

All record types validate their content on construction.

### ARecord

::: oinker.ARecord

### AAAARecord

::: oinker.AAAARecord

### MXRecord

::: oinker.MXRecord

### TXTRecord

::: oinker.TXTRecord

### CNAMERecord

::: oinker.CNAMERecord

### ALIASRecord

::: oinker.ALIASRecord

### NSRecord

::: oinker.NSRecord

### SRVRecord

::: oinker.SRVRecord

### TLSARecord

::: oinker.TLSARecord

### CAARecord

::: oinker.CAARecord

### HTTPSRecord

::: oinker.HTTPSRecord

### SVCBRecord

::: oinker.SVCBRecord

### SSHFPRecord

::: oinker.SSHFPRecord

## Response Types

### DNSRecordResponse

::: oinker.DNSRecordResponse
