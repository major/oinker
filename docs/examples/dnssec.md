# DNSSEC

This page covers DNSSEC (DNS Security Extensions) operations for managing DS records at the registry level.

## Quick Start

=== "Async"

    ```python
    from oinker import AsyncPiglet, DNSSECRecordCreate

    async with AsyncPiglet() as piglet:
        # List existing DNSSEC records
        records = await piglet.dnssec.list("example.com")
        for record in records:
            print(f"Key Tag: {record.key_tag}, Algorithm: {record.algorithm}")

        # Create a new DNSSEC record
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

=== "Sync"

    ```python
    from oinker import Piglet, DNSSECRecordCreate

    with Piglet() as piglet:
        # List existing DNSSEC records
        records = piglet.dnssec.list("example.com")
        for record in records:
            print(f"Key Tag: {record.key_tag}, Algorithm: {record.algorithm}")

        # Create a new DNSSEC record
        piglet.dnssec.create(
            "example.com",
            DNSSECRecordCreate(
                key_tag="64087",
                algorithm="13",
                digest_type="2",
                digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
            )
        )
    ```

---

## List DNSSEC Records

Retrieve all DNSSEC DS records for a domain from the registry.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        records = await piglet.dnssec.list("example.com")

        if not records:
            print("No DNSSEC records configured")
        else:
            print(f"Found {len(records)} DNSSEC record(s):")
            for record in records:
                print(f"  Key Tag: {record.key_tag}")
                print(f"  Algorithm: {record.algorithm}")
                print(f"  Digest Type: {record.digest_type}")
                print(f"  Digest: {record.digest[:32]}...")
                print("  ---")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        records = piglet.dnssec.list("example.com")

        if not records:
            print("No DNSSEC records configured")
        else:
            print(f"Found {len(records)} DNSSEC record(s):")
            for record in records:
                print(f"  Key Tag: {record.key_tag}")
                print(f"  Algorithm: {record.algorithm}")
                print(f"  Digest Type: {record.digest_type}")
                print(f"  Digest: {record.digest[:32]}...")
                print("  ---")
    ```

---

## Create DNSSEC Record

Create a DS record at the registry to enable DNSSEC.

!!! info "Common Algorithm Values"
    - `8` - RSA/SHA-256
    - `13` - ECDSA Curve P-256 with SHA-256 (recommended)
    - `14` - ECDSA Curve P-384 with SHA-384
    - `15` - Ed25519

!!! info "Common Digest Type Values"
    - `1` - SHA-1 (deprecated)
    - `2` - SHA-256 (recommended)
    - `4` - SHA-384

### Basic DS Record

=== "Async"

    ```python
    from oinker import AsyncPiglet, DNSSECRecordCreate

    async with AsyncPiglet() as piglet:
        # Standard DS record (most common case)
        await piglet.dnssec.create(
            "example.com",
            DNSSECRecordCreate(
                key_tag="64087",
                algorithm="13",      # ECDSAP256SHA256
                digest_type="2",     # SHA-256
                digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
            )
        )
        print("DNSSEC record created!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet, DNSSECRecordCreate

    with Piglet() as piglet:
        # Standard DS record (most common case)
        piglet.dnssec.create(
            "example.com",
            DNSSECRecordCreate(
                key_tag="64087",
                algorithm="13",      # ECDSAP256SHA256
                digest_type="2",     # SHA-256
                digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
            )
        )
        print("DNSSEC record created!")
    ```

### With Optional Key Data

Some registries require additional key data fields:

=== "Async"

    ```python
    from oinker import AsyncPiglet, DNSSECRecordCreate

    async with AsyncPiglet() as piglet:
        await piglet.dnssec.create(
            "example.com",
            DNSSECRecordCreate(
                # Required DS data
                key_tag="64087",
                algorithm="13",
                digest_type="2",
                digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
                # Optional key data (rarely needed)
                max_sig_life="86400",
                key_data_flags="257",
                key_data_protocol="3",
                key_data_algorithm="13",
                key_data_public_key="mdsswUyr3DPW132mOi8V9xESWE8jTo0dxCjjnopKl+GqJxpVXckHAeF+KkxLbxILfDLUT0rAK9iUzy1L53eKGQ==",
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, DNSSECRecordCreate

    with Piglet() as piglet:
        piglet.dnssec.create(
            "example.com",
            DNSSECRecordCreate(
                # Required DS data
                key_tag="64087",
                algorithm="13",
                digest_type="2",
                digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC",
                # Optional key data (rarely needed)
                max_sig_life="86400",
                key_data_flags="257",
                key_data_protocol="3",
                key_data_algorithm="13",
                key_data_public_key="mdsswUyr3DPW132mOi8V9xESWE8jTo0dxCjjnopKl+GqJxpVXckHAeF+KkxLbxILfDLUT0rAK9iUzy1L53eKGQ==",
            )
        )
    ```

---

## Delete DNSSEC Record

Delete a DS record from the registry.

!!! warning "Registry Behavior"
    Most registries will delete all DNSSEC records with matching data, not just the record with the matching key tag.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        await piglet.dnssec.delete("example.com", key_tag="64087")
        print("DNSSEC record deleted!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        piglet.dnssec.delete("example.com", key_tag="64087")
        print("DNSSEC record deleted!")
    ```

---

## Real-World Patterns

### Enable DNSSEC for a Domain

Complete workflow for enabling DNSSEC:

=== "Async"

    ```python
    from oinker import AsyncPiglet, DNSSECRecordCreate

    async with AsyncPiglet() as piglet:
        domain = "example.com"

        # 1. Check if DNSSEC is already enabled
        existing = await piglet.dnssec.list(domain)

        if existing:
            print(f"DNSSEC already enabled with {len(existing)} record(s)")
            for record in existing:
                print(f"  Key Tag: {record.key_tag}")
            return

        # 2. Get DS record from your DNS provider
        # (This example uses placeholder values - get real ones from your provider)
        ds_record = DNSSECRecordCreate(
            key_tag="12345",
            algorithm="13",
            digest_type="2",
            digest="ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890",
        )

        # 3. Create the DS record at the registry
        await piglet.dnssec.create(domain, ds_record)
        print(f"✅ DNSSEC enabled for {domain}")

        # 4. Verify it was created
        records = await piglet.dnssec.list(domain)
        print(f"   {len(records)} DS record(s) now active")
    ```

=== "Sync"

    ```python
    from oinker import Piglet, DNSSECRecordCreate

    with Piglet() as piglet:
        domain = "example.com"

        # 1. Check if DNSSEC is already enabled
        existing = piglet.dnssec.list(domain)

        if existing:
            print(f"DNSSEC already enabled with {len(existing)} record(s)")
            for record in existing:
                print(f"  Key Tag: {record.key_tag}")
            return

        # 2. Get DS record from your DNS provider
        # (This example uses placeholder values - get real ones from your provider)
        ds_record = DNSSECRecordCreate(
            key_tag="12345",
            algorithm="13",
            digest_type="2",
            digest="ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890",
        )

        # 3. Create the DS record at the registry
        piglet.dnssec.create(domain, ds_record)
        print(f"✅ DNSSEC enabled for {domain}")

        # 4. Verify it was created
        records = piglet.dnssec.list(domain)
        print(f"   {len(records)} DS record(s) now active")
    ```

### Disable DNSSEC for a Domain

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        domain = "example.com"

        # Get all DNSSEC records
        records = await piglet.dnssec.list(domain)

        if not records:
            print(f"DNSSEC is not enabled for {domain}")
            return

        # Delete all DS records
        for record in records:
            await piglet.dnssec.delete(domain, key_tag=record.key_tag)
            print(f"Deleted DS record with key tag: {record.key_tag}")

        print(f"✅ DNSSEC disabled for {domain}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        domain = "example.com"

        # Get all DNSSEC records
        records = piglet.dnssec.list(domain)

        if not records:
            print(f"DNSSEC is not enabled for {domain}")
            return

        # Delete all DS records
        for record in records:
            piglet.dnssec.delete(domain, key_tag=record.key_tag)
            print(f"Deleted DS record with key tag: {record.key_tag}")

        print(f"✅ DNSSEC disabled for {domain}")
    ```

### Audit DNSSEC Status Across Domains

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        domains = await piglet.domains.list()

        print("DNSSEC Status Report")
        print("=" * 50)

        enabled = []
        disabled = []

        for domain_info in domains:
            domain = domain_info.domain
            try:
                records = await piglet.dnssec.list(domain)
                if records:
                    enabled.append((domain, len(records)))
                else:
                    disabled.append(domain)
            except Exception as e:
                print(f"⚠️ {domain}: Error checking DNSSEC - {e}")

        print(f"\n✅ DNSSEC Enabled ({len(enabled)} domains):")
        for domain, count in enabled:
            print(f"   {domain} ({count} DS record(s))")

        print(f"\n❌ DNSSEC Disabled ({len(disabled)} domains):")
        for domain in disabled:
            print(f"   {domain}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        domains = piglet.domains.list()

        print("DNSSEC Status Report")
        print("=" * 50)

        enabled = []
        disabled = []

        for domain_info in domains:
            domain = domain_info.domain
            try:
                records = piglet.dnssec.list(domain)
                if records:
                    enabled.append((domain, len(records)))
                else:
                    disabled.append(domain)
            except Exception as e:
                print(f"⚠️ {domain}: Error checking DNSSEC - {e}")

        print(f"\n✅ DNSSEC Enabled ({len(enabled)} domains):")
        for domain, count in enabled:
            print(f"   {domain} ({count} DS record(s))")

        print(f"\n❌ DNSSEC Disabled ({len(disabled)} domains):")
        for domain in disabled:
            print(f"   {domain}")
    ```
