# DNS Records

This page covers all DNS record operations with examples for every supported record type.

## Quick Start

=== "Async"

    ```python
    from oinker import AsyncPiglet, ARecord

    async with AsyncPiglet() as piglet:
        # List all records
        records = await piglet.dns.list("example.com")
        for record in records:
            print(f"{record.record_type} {record.name} -> {record.content}")

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
        # List all records
        records = piglet.dns.list("example.com")
        for record in records:
            print(f"{record.record_type} {record.name} -> {record.content}")

        # Create an A record
        record_id = piglet.dns.create(
            "example.com",
            ARecord(content="1.2.3.4", name="www")
        )
        print(f"Created record: {record_id}")
    ```

---

## List Records

Retrieve all DNS records for a domain.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        records = await piglet.dns.list("example.com")

        for record in records:
            print(f"ID: {record.id}")
            print(f"Type: {record.record_type}")
            print(f"Name: {record.name}")
            print(f"Content: {record.content}")
            print(f"TTL: {record.ttl}")
            print(f"Priority: {record.priority}")
            print("---")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        records = piglet.dns.list("example.com")

        for record in records:
            print(f"ID: {record.id}")
            print(f"Type: {record.record_type}")
            print(f"Name: {record.name}")
            print(f"Content: {record.content}")
            print(f"TTL: {record.ttl}")
            print(f"Priority: {record.priority}")
            print("---")
    ```

---

## Get a Single Record

### By Record ID

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        record = await piglet.dns.get("example.com", record_id="123456789")

        if record:
            print(f"{record.record_type} {record.name} -> {record.content}")
        else:
            print("Record not found")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        record = piglet.dns.get("example.com", record_id="123456789")

        if record:
            print(f"{record.record_type} {record.name} -> {record.content}")
        else:
            print("Record not found")
    ```

### By Name and Type

=== "Async"

    ```python
    from oinker import AsyncPiglet

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

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Get all A records for www subdomain
        records = piglet.dns.get_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www"
        )

        for record in records:
            print(f"{record.name} -> {record.content}")

        # Get root domain A records (no subdomain)
        root_records = piglet.dns.get_by_name_type(
            "example.com",
            record_type="A"
        )
    ```

---

## Create Records

### A Record (IPv4)

=== "Async"

    ```python
    from oinker import AsyncPiglet, ARecord

    async with AsyncPiglet() as piglet:
        # www subdomain
        record_id = await piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34", name="www")
        )

        # Root domain (no name)
        record_id = await piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34")
        )

        # With custom TTL
        record_id = await piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34", name="api", ttl=3600)
        )

        # Wildcard record
        record_id = await piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34", name="*")
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ARecord

    with Piglet() as piglet:
        # www subdomain
        record_id = piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34", name="www")
        )

        # Root domain (no name)
        record_id = piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34")
        )

        # With custom TTL
        record_id = piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34", name="api", ttl=3600)
        )

        # Wildcard record
        record_id = piglet.dns.create(
            "example.com",
            ARecord(content="93.184.216.34", name="*")
        )
    ```

### AAAA Record (IPv6)

=== "Async"

    ```python
    from oinker import AsyncPiglet, AAAARecord

    async with AsyncPiglet() as piglet:
        record_id = await piglet.dns.create(
            "example.com",
            AAAARecord(
                content="2606:2800:220:1:248:1893:25c8:1946",
                name="www"
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, AAAARecord

    with Piglet() as piglet:
        record_id = piglet.dns.create(
            "example.com",
            AAAARecord(
                content="2606:2800:220:1:248:1893:25c8:1946",
                name="www"
            )
        )
    ```

### MX Record (Mail)

=== "Async"

    ```python
    from oinker import AsyncPiglet, MXRecord

    async with AsyncPiglet() as piglet:
        # Primary mail server
        await piglet.dns.create(
            "example.com",
            MXRecord(content="mail.example.com", priority=10)
        )

        # Backup mail server
        await piglet.dns.create(
            "example.com",
            MXRecord(content="mail2.example.com", priority=20)
        )

        # Google Workspace
        await piglet.dns.create(
            "example.com",
            MXRecord(content="aspmx.l.google.com", priority=1)
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, MXRecord

    with Piglet() as piglet:
        # Primary mail server
        piglet.dns.create(
            "example.com",
            MXRecord(content="mail.example.com", priority=10)
        )

        # Backup mail server
        piglet.dns.create(
            "example.com",
            MXRecord(content="mail2.example.com", priority=20)
        )

        # Google Workspace
        piglet.dns.create(
            "example.com",
            MXRecord(content="aspmx.l.google.com", priority=1)
        )
    ```

### TXT Record

=== "Async"

    ```python
    from oinker import AsyncPiglet, TXTRecord

    async with AsyncPiglet() as piglet:
        # SPF record
        await piglet.dns.create(
            "example.com",
            TXTRecord(content="v=spf1 include:_spf.google.com ~all")
        )

        # DKIM record
        await piglet.dns.create(
            "example.com",
            TXTRecord(
                content="v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEB...",
                name="google._domainkey"
            )
        )

        # DMARC record
        await piglet.dns.create(
            "example.com",
            TXTRecord(
                content="v=DMARC1; p=reject; rua=mailto:dmarc@example.com",
                name="_dmarc"
            )
        )

        # Domain verification
        await piglet.dns.create(
            "example.com",
            TXTRecord(content="google-site-verification=abc123...")
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, TXTRecord

    with Piglet() as piglet:
        # SPF record
        piglet.dns.create(
            "example.com",
            TXTRecord(content="v=spf1 include:_spf.google.com ~all")
        )

        # DKIM record
        piglet.dns.create(
            "example.com",
            TXTRecord(
                content="v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEB...",
                name="google._domainkey"
            )
        )

        # DMARC record
        piglet.dns.create(
            "example.com",
            TXTRecord(
                content="v=DMARC1; p=reject; rua=mailto:dmarc@example.com",
                name="_dmarc"
            )
        )

        # Domain verification
        piglet.dns.create(
            "example.com",
            TXTRecord(content="google-site-verification=abc123...")
        )
    ```

### CNAME Record

=== "Async"

    ```python
    from oinker import AsyncPiglet, CNAMERecord

    async with AsyncPiglet() as piglet:
        # Point blog to external service
        await piglet.dns.create(
            "example.com",
            CNAMERecord(content="example.ghost.io", name="blog")
        )

        # Point www to root
        await piglet.dns.create(
            "example.com",
            CNAMERecord(content="example.com", name="www")
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, CNAMERecord

    with Piglet() as piglet:
        # Point blog to external service
        piglet.dns.create(
            "example.com",
            CNAMERecord(content="example.ghost.io", name="blog")
        )

        # Point www to root
        piglet.dns.create(
            "example.com",
            CNAMERecord(content="example.com", name="www")
        )
    ```

### ALIAS Record

ALIAS records work like CNAME but can be used at the zone apex (root domain).

=== "Async"

    ```python
    from oinker import AsyncPiglet, ALIASRecord

    async with AsyncPiglet() as piglet:
        # Point root domain to load balancer
        await piglet.dns.create(
            "example.com",
            ALIASRecord(content="lb.example.com")
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ALIASRecord

    with Piglet() as piglet:
        # Point root domain to load balancer
        piglet.dns.create(
            "example.com",
            ALIASRecord(content="lb.example.com")
        )
    ```

### NS Record

=== "Async"

    ```python
    from oinker import AsyncPiglet, NSRecord

    async with AsyncPiglet() as piglet:
        # Delegate subdomain to different nameservers
        await piglet.dns.create(
            "example.com",
            NSRecord(content="ns1.subdomain-host.com", name="subdomain")
        )
        await piglet.dns.create(
            "example.com",
            NSRecord(content="ns2.subdomain-host.com", name="subdomain")
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, NSRecord

    with Piglet() as piglet:
        # Delegate subdomain to different nameservers
        piglet.dns.create(
            "example.com",
            NSRecord(content="ns1.subdomain-host.com", name="subdomain")
        )
        piglet.dns.create(
            "example.com",
            NSRecord(content="ns2.subdomain-host.com", name="subdomain")
        )
    ```

### SRV Record

=== "Async"

    ```python
    from oinker import AsyncPiglet, SRVRecord

    async with AsyncPiglet() as piglet:
        # SIP service
        await piglet.dns.create(
            "example.com",
            SRVRecord(
                content="10 5 5060 sip.example.com",  # priority weight port target
                name="_sip._tcp"
            )
        )

        # XMPP/Jabber
        await piglet.dns.create(
            "example.com",
            SRVRecord(
                content="5 0 5222 xmpp.example.com",
                name="_xmpp-client._tcp"
            )
        )

        # Microsoft 365
        await piglet.dns.create(
            "example.com",
            SRVRecord(
                content="100 1 443 sipdir.online.lync.com",
                name="_sipfederationtls._tcp"
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, SRVRecord

    with Piglet() as piglet:
        # SIP service
        piglet.dns.create(
            "example.com",
            SRVRecord(
                content="10 5 5060 sip.example.com",  # priority weight port target
                name="_sip._tcp"
            )
        )

        # XMPP/Jabber
        piglet.dns.create(
            "example.com",
            SRVRecord(
                content="5 0 5222 xmpp.example.com",
                name="_xmpp-client._tcp"
            )
        )

        # Microsoft 365
        piglet.dns.create(
            "example.com",
            SRVRecord(
                content="100 1 443 sipdir.online.lync.com",
                name="_sipfederationtls._tcp"
            )
        )
    ```

### CAA Record

CAA records specify which certificate authorities can issue certificates for your domain.

=== "Async"

    ```python
    from oinker import AsyncPiglet, CAARecord

    async with AsyncPiglet() as piglet:
        # Allow Let's Encrypt
        await piglet.dns.create(
            "example.com",
            CAARecord(content='0 issue "letsencrypt.org"')
        )

        # Allow wildcard from specific CA
        await piglet.dns.create(
            "example.com",
            CAARecord(content='0 issuewild "digicert.com"')
        )

        # Report violations
        await piglet.dns.create(
            "example.com",
            CAARecord(content='0 iodef "mailto:security@example.com"')
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, CAARecord

    with Piglet() as piglet:
        # Allow Let's Encrypt
        piglet.dns.create(
            "example.com",
            CAARecord(content='0 issue "letsencrypt.org"')
        )

        # Allow wildcard from specific CA
        piglet.dns.create(
            "example.com",
            CAARecord(content='0 issuewild "digicert.com"')
        )

        # Report violations
        piglet.dns.create(
            "example.com",
            CAARecord(content='0 iodef "mailto:security@example.com"')
        )
    ```

### TLSA Record (DANE)

TLSA records enable DNS-based Authentication of Named Entities (DANE).

=== "Async"

    ```python
    from oinker import AsyncPiglet, TLSARecord

    async with AsyncPiglet() as piglet:
        # DANE for HTTPS
        await piglet.dns.create(
            "example.com",
            TLSARecord(
                content="3 1 1 2bb183af273adee...",  # usage selector matching_type cert_data
                name="_443._tcp.www"
            )
        )

        # DANE for SMTP
        await piglet.dns.create(
            "example.com",
            TLSARecord(
                content="3 1 1 abc123def456...",
                name="_25._tcp.mail"
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, TLSARecord

    with Piglet() as piglet:
        # DANE for HTTPS
        piglet.dns.create(
            "example.com",
            TLSARecord(
                content="3 1 1 2bb183af273adee...",  # usage selector matching_type cert_data
                name="_443._tcp.www"
            )
        )

        # DANE for SMTP
        piglet.dns.create(
            "example.com",
            TLSARecord(
                content="3 1 1 abc123def456...",
                name="_25._tcp.mail"
            )
        )
    ```

### HTTPS Record

HTTPS records provide connection parameters for HTTPS services.

=== "Async"

    ```python
    from oinker import AsyncPiglet, HTTPSRecord

    async with AsyncPiglet() as piglet:
        # Basic HTTPS record
        await piglet.dns.create(
            "example.com",
            HTTPSRecord(content="1 . alpn=h2,h3")
        )

        # With ECH (Encrypted Client Hello)
        await piglet.dns.create(
            "example.com",
            HTTPSRecord(
                content='1 . alpn=h2,h3 ech="..."',
                name="www"
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, HTTPSRecord

    with Piglet() as piglet:
        # Basic HTTPS record
        piglet.dns.create(
            "example.com",
            HTTPSRecord(content="1 . alpn=h2,h3")
        )

        # With ECH (Encrypted Client Hello)
        piglet.dns.create(
            "example.com",
            HTTPSRecord(
                content='1 . alpn=h2,h3 ech="..."',
                name="www"
            )
        )
    ```

### SVCB Record

SVCB records provide service binding information.

=== "Async"

    ```python
    from oinker import AsyncPiglet, SVCBRecord

    async with AsyncPiglet() as piglet:
        await piglet.dns.create(
            "example.com",
            SVCBRecord(
                content="1 . alpn=h2,h3 port=8443",
                name="_api"
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, SVCBRecord

    with Piglet() as piglet:
        piglet.dns.create(
            "example.com",
            SVCBRecord(
                content="1 . alpn=h2,h3 port=8443",
                name="_api"
            )
        )
    ```

### SSHFP Record

SSHFP records publish SSH host key fingerprints in DNS.

=== "Async"

    ```python
    from oinker import AsyncPiglet, SSHFPRecord

    async with AsyncPiglet() as piglet:
        # RSA key with SHA-256
        await piglet.dns.create(
            "example.com",
            SSHFPRecord(
                content="1 2 abc123def456...",  # algorithm fp_type fingerprint
                name="server"
            )
        )

        # Ed25519 key with SHA-256
        await piglet.dns.create(
            "example.com",
            SSHFPRecord(
                content="4 2 789xyz...",
                name="server"
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, SSHFPRecord

    with Piglet() as piglet:
        # RSA key with SHA-256
        piglet.dns.create(
            "example.com",
            SSHFPRecord(
                content="1 2 abc123def456...",  # algorithm fp_type fingerprint
                name="server"
            )
        )

        # Ed25519 key with SHA-256
        piglet.dns.create(
            "example.com",
            SSHFPRecord(
                content="4 2 789xyz...",
                name="server"
            )
        )
    ```

---

## Edit Records

### By Record ID

=== "Async"

    ```python
    from oinker import AsyncPiglet, ARecord

    async with AsyncPiglet() as piglet:
        await piglet.dns.edit(
            "example.com",
            record_id="123456789",
            record=ARecord(content="5.6.7.8", name="www")
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ARecord

    with Piglet() as piglet:
        piglet.dns.edit(
            "example.com",
            record_id="123456789",
            record=ARecord(content="5.6.7.8", name="www")
        )
    ```

### By Name and Type

Updates all records matching the subdomain and type.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Update all www A records
        await piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www",
            content="5.6.7.8"
        )

        # Update with TTL and notes
        await piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            subdomain="api",
            content="10.0.0.1",
            ttl=3600,
            notes="Production API server"
        )

        # Update root domain records
        await piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            content="5.6.7.8"
        )

        # Clear notes (empty string clears, None leaves unchanged)
        await piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www",
            content="5.6.7.8",
            notes=""
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Update all www A records
        piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www",
            content="5.6.7.8"
        )

        # Update with TTL and notes
        piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            subdomain="api",
            content="10.0.0.1",
            ttl=3600,
            notes="Production API server"
        )

        # Update root domain records
        piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            content="5.6.7.8"
        )

        # Clear notes (empty string clears, None leaves unchanged)
        piglet.dns.edit_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www",
            content="5.6.7.8",
            notes=""
        )
    ```

---

## Delete Records

### By Record ID

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        await piglet.dns.delete("example.com", record_id="123456789")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        piglet.dns.delete("example.com", record_id="123456789")
    ```

### By Name and Type

Deletes all records matching the subdomain and type.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Delete all www A records
        await piglet.dns.delete_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www"
        )

        # Delete root domain A records
        await piglet.dns.delete_by_name_type(
            "example.com",
            record_type="A"
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Delete all www A records
        piglet.dns.delete_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www"
        )

        # Delete root domain A records
        piglet.dns.delete_by_name_type(
            "example.com",
            record_type="A"
        )
    ```

---

## Real-World Patterns

### Bulk Record Creation

=== "Async"

    ```python
    import asyncio
    from oinker import AsyncPiglet, ARecord, AAAARecord, MXRecord, TXTRecord

    async with AsyncPiglet() as piglet:
        records = [
            ARecord(content="93.184.216.34"),
            ARecord(content="93.184.216.34", name="www"),
            AAAARecord(content="2606:2800:220:1:248:1893:25c8:1946"),
            MXRecord(content="mail.example.com", priority=10),
            TXTRecord(content="v=spf1 include:_spf.google.com ~all"),
        ]

        # Create all records concurrently
        tasks = [
            piglet.dns.create("example.com", record)
            for record in records
        ]
        record_ids = await asyncio.gather(*tasks)
        print(f"Created {len(record_ids)} records")
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ARecord, AAAARecord, MXRecord, TXTRecord

    with Piglet() as piglet:
        records = [
            ARecord(content="93.184.216.34"),
            ARecord(content="93.184.216.34", name="www"),
            AAAARecord(content="2606:2800:220:1:248:1893:25c8:1946"),
            MXRecord(content="mail.example.com", priority=10),
            TXTRecord(content="v=spf1 include:_spf.google.com ~all"),
        ]

        record_ids = []
        for record in records:
            record_id = piglet.dns.create("example.com", record)
            record_ids.append(record_id)

        print(f"Created {len(record_ids)} records")
    ```

### Find and Update a Record

=== "Async"

    ```python
    from oinker import AsyncPiglet, ARecord

    async with AsyncPiglet() as piglet:
        # Find the www A record
        records = await piglet.dns.get_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www"
        )

        if records:
            # Update it
            await piglet.dns.edit(
                "example.com",
                record_id=records[0].id,
                record=ARecord(content="5.6.7.8", name="www")
            )
            print(f"Updated record {records[0].id}")
        else:
            # Create it if it doesn't exist
            record_id = await piglet.dns.create(
                "example.com",
                ARecord(content="5.6.7.8", name="www")
            )
            print(f"Created record {record_id}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ARecord

    with Piglet() as piglet:
        # Find the www A record
        records = piglet.dns.get_by_name_type(
            "example.com",
            record_type="A",
            subdomain="www"
        )

        if records:
            # Update it
            piglet.dns.edit(
                "example.com",
                record_id=records[0].id,
                record=ARecord(content="5.6.7.8", name="www")
            )
            print(f"Updated record {records[0].id}")
        else:
            # Create it if it doesn't exist
            record_id = piglet.dns.create(
                "example.com",
                ARecord(content="5.6.7.8", name="www")
            )
            print(f"Created record {record_id}")
    ```

### Delete All Records of a Type

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Get all TXT records
        records = await piglet.dns.list("example.com")
        txt_records = [r for r in records if r.record_type == "TXT"]

        # Delete them all
        for record in txt_records:
            await piglet.dns.delete("example.com", record_id=record.id)
            print(f"Deleted TXT record: {record.content[:50]}...")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Get all TXT records
        records = piglet.dns.list("example.com")
        txt_records = [r for r in records if r.record_type == "TXT"]

        # Delete them all
        for record in txt_records:
            piglet.dns.delete("example.com", record_id=record.id)
            print(f"Deleted TXT record: {record.content[:50]}...")
    ```

### Migrate Records Between Domains

=== "Async"

    ```python
    from oinker import AsyncPiglet, ARecord, AAAARecord, MXRecord, TXTRecord, CNAMERecord

    async with AsyncPiglet() as piglet:
        # Get all records from source domain
        source_records = await piglet.dns.list("old-domain.com")

        # Map record types to dataclasses
        record_classes = {
            "A": ARecord,
            "AAAA": AAAARecord,
            "MX": MXRecord,
            "TXT": TXTRecord,
            "CNAME": CNAMERecord,
        }

        for record in source_records:
            record_class = record_classes.get(record.record_type)
            if not record_class:
                print(f"Skipping unsupported type: {record.record_type}")
                continue

            # Extract subdomain from full name
            subdomain = record.name.replace(".old-domain.com", "")
            if subdomain == "old-domain.com":
                subdomain = None

            # Build the new record
            kwargs = {"content": record.content, "ttl": record.ttl}
            if subdomain:
                kwargs["name"] = subdomain
            if record.priority:
                kwargs["priority"] = record.priority

            new_record = record_class(**kwargs)

            # Create on new domain
            await piglet.dns.create("new-domain.com", new_record)
            print(f"Migrated: {record.record_type} {record.name}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet, ARecord, AAAARecord, MXRecord, TXTRecord, CNAMERecord

    with Piglet() as piglet:
        # Get all records from source domain
        source_records = piglet.dns.list("old-domain.com")

        # Map record types to dataclasses
        record_classes = {
            "A": ARecord,
            "AAAA": AAAARecord,
            "MX": MXRecord,
            "TXT": TXTRecord,
            "CNAME": CNAMERecord,
        }

        for record in source_records:
            record_class = record_classes.get(record.record_type)
            if not record_class:
                print(f"Skipping unsupported type: {record.record_type}")
                continue

            # Extract subdomain from full name
            subdomain = record.name.replace(".old-domain.com", "")
            if subdomain == "old-domain.com":
                subdomain = None

            # Build the new record
            kwargs = {"content": record.content, "ttl": record.ttl}
            if subdomain:
                kwargs["name"] = subdomain
            if record.priority:
                kwargs["priority"] = record.priority

            new_record = record_class(**kwargs)

            # Create on new domain
            piglet.dns.create("new-domain.com", new_record)
            print(f"Migrated: {record.record_type} {record.name}")
    ```
