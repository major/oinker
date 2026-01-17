# Domains

This page covers domain management operations: listing domains, nameservers, URL forwarding, glue records, and availability checks.

## Quick Start

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # List all domains
        domains = await piglet.domains.list()
        for domain in domains:
            print(f"{domain.domain} - expires {domain.expire_date}")

        # Check domain availability
        availability = await piglet.domains.check("coolname.com")
        if availability.available:
            print(f"Available for ${availability.pricing.registration}!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # List all domains
        domains = piglet.domains.list()
        for domain in domains:
            print(f"{domain.domain} - expires {domain.expire_date}")

        # Check domain availability
        availability = piglet.domains.check("coolname.com")
        if availability.available:
            print(f"Available for ${availability.pricing.registration}!")
    ```

---

## List Domains

List all domains in your Porkbun account.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Basic listing
        domains = await piglet.domains.list()

        for domain in domains:
            print(f"Domain: {domain.domain}")
            print(f"  Status: {domain.status}")
            print(f"  Created: {domain.create_date}")
            print(f"  Expires: {domain.expire_date}")
            print(f"  Auto-renew: {domain.auto_renew}")
            print(f"  WHOIS Privacy: {domain.whois_privacy}")
            print(f"  Security Lock: {domain.security_lock}")
            print("---")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Basic listing
        domains = piglet.domains.list()

        for domain in domains:
            print(f"Domain: {domain.domain}")
            print(f"  Status: {domain.status}")
            print(f"  Created: {domain.create_date}")
            print(f"  Expires: {domain.expire_date}")
            print(f"  Auto-renew: {domain.auto_renew}")
            print(f"  WHOIS Privacy: {domain.whois_privacy}")
            print(f"  Security Lock: {domain.security_lock}")
            print("---")
    ```

### With Labels

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Include label information
        domains = await piglet.domains.list(include_labels=True)

        for domain in domains:
            if domain.labels:
                labels = ", ".join(label.title for label in domain.labels)
                print(f"{domain.domain} [{labels}]")
            else:
                print(f"{domain.domain} [no labels]")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Include label information
        domains = piglet.domains.list(include_labels=True)

        for domain in domains:
            if domain.labels:
                labels = ", ".join(label.title for label in domain.labels)
                print(f"{domain.domain} [{labels}]")
            else:
                print(f"{domain.domain} [no labels]")
    ```

### Pagination (1000+ Domains)

Domains are returned in chunks of 1000. Use pagination for large accounts:

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        all_domains = []
        start = 0

        while True:
            batch = await piglet.domains.list(start=start)
            if not batch:
                break
            all_domains.extend(batch)
            start += 1000

        print(f"Total domains: {len(all_domains)}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        all_domains = []
        start = 0

        while True:
            batch = piglet.domains.list(start=start)
            if not batch:
                break
            all_domains.extend(batch)
            start += 1000

        print(f"Total domains: {len(all_domains)}")
    ```

---

## Nameservers

### Get Nameservers

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        nameservers = await piglet.domains.get_nameservers("example.com")

        print("Current nameservers:")
        for ns in nameservers:
            print(f"  {ns}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        nameservers = piglet.domains.get_nameservers("example.com")

        print("Current nameservers:")
        for ns in nameservers:
            print(f"  {ns}")
    ```

### Update Nameservers

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Use custom nameservers
        await piglet.domains.update_nameservers(
            "example.com",
            [
                "ns1.example.com",
                "ns2.example.com",
            ]
        )
        print("Nameservers updated!")

        # Switch to Cloudflare
        await piglet.domains.update_nameservers(
            "example.com",
            [
                "nova.ns.cloudflare.com",
                "zara.ns.cloudflare.com",
            ]
        )

        # Switch back to Porkbun
        await piglet.domains.update_nameservers(
            "example.com",
            [
                "curitiba.ns.porkbun.com",
                "fortaleza.ns.porkbun.com",
                "maceio.ns.porkbun.com",
                "salvador.ns.porkbun.com",
            ]
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # Use custom nameservers
        piglet.domains.update_nameservers(
            "example.com",
            [
                "ns1.example.com",
                "ns2.example.com",
            ]
        )
        print("Nameservers updated!")

        # Switch to Cloudflare
        piglet.domains.update_nameservers(
            "example.com",
            [
                "nova.ns.cloudflare.com",
                "zara.ns.cloudflare.com",
            ]
        )

        # Switch back to Porkbun
        piglet.domains.update_nameservers(
            "example.com",
            [
                "curitiba.ns.porkbun.com",
                "fortaleza.ns.porkbun.com",
                "maceio.ns.porkbun.com",
                "salvador.ns.porkbun.com",
            ]
        )
    ```

---

## URL Forwarding

### List URL Forwards

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        forwards = await piglet.domains.get_url_forwards("example.com")

        for forward in forwards:
            subdomain = forward.subdomain or "@"
            print(f"ID: {forward.id}")
            print(f"  {subdomain}.example.com -> {forward.location}")
            print(f"  Type: {forward.type}")
            print(f"  Include path: {forward.include_path}")
            print(f"  Wildcard: {forward.wildcard}")
            print("---")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        forwards = piglet.domains.get_url_forwards("example.com")

        for forward in forwards:
            subdomain = forward.subdomain or "@"
            print(f"ID: {forward.id}")
            print(f"  {subdomain}.example.com -> {forward.location}")
            print(f"  Type: {forward.type}")
            print(f"  Include path: {forward.include_path}")
            print(f"  Wildcard: {forward.wildcard}")
            print("---")
    ```

### Add URL Forward

=== "Async"

    ```python
    from oinker import AsyncPiglet, URLForwardCreate

    async with AsyncPiglet() as piglet:
        # Simple redirect (root domain)
        await piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                location="https://www.example.com",
                type="permanent",
            )
        )

        # Subdomain redirect
        await piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                subdomain="blog",
                location="https://blog.example.com",
                type="permanent",
            )
        )

        # Temporary redirect with path preservation
        await piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                subdomain="old",
                location="https://new.example.com",
                type="temporary",
                include_path=True,
            )
        )

        # Wildcard redirect (all subdomains)
        await piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                location="https://main.example.com",
                type="permanent",
                wildcard=True,
            )
        )
    ```

=== "Sync"

    ```python
    from oinker import Piglet, URLForwardCreate

    with Piglet() as piglet:
        # Simple redirect (root domain)
        piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                location="https://www.example.com",
                type="permanent",
            )
        )

        # Subdomain redirect
        piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                subdomain="blog",
                location="https://blog.example.com",
                type="permanent",
            )
        )

        # Temporary redirect with path preservation
        piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                subdomain="old",
                location="https://new.example.com",
                type="temporary",
                include_path=True,
            )
        )

        # Wildcard redirect (all subdomains)
        piglet.domains.add_url_forward(
            "example.com",
            URLForwardCreate(
                location="https://main.example.com",
                type="permanent",
                wildcard=True,
            )
        )
    ```

### Delete URL Forward

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # First, get the forward ID
        forwards = await piglet.domains.get_url_forwards("example.com")

        for forward in forwards:
            if forward.subdomain == "old":
                await piglet.domains.delete_url_forward(
                    "example.com",
                    forward_id=forward.id
                )
                print(f"Deleted forward: {forward.id}")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # First, get the forward ID
        forwards = piglet.domains.get_url_forwards("example.com")

        for forward in forwards:
            if forward.subdomain == "old":
                piglet.domains.delete_url_forward(
                    "example.com",
                    forward_id=forward.id
                )
                print(f"Deleted forward: {forward.id}")
    ```

---

## Domain Availability

Check if a domain is available for registration.

!!! warning "Rate Limited"
    Domain checks are rate limited by Porkbun. The response includes rate limit information.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        availability = await piglet.domains.check("coolname.com")

        if availability.available:
            print(f"✅ coolname.com is available!")
            print(f"   Registration: ${availability.pricing.registration}")
            print(f"   Renewal: ${availability.pricing.renewal}")
            print(f"   Transfer: ${availability.pricing.transfer}")

            if availability.first_year_promo:
                print(f"   🎉 First year promo! Regular: ${availability.regular_price}")
        else:
            print("❌ coolname.com is taken")

        if availability.premium:
            print("   ⭐ This is a premium domain")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        availability = piglet.domains.check("coolname.com")

        if availability.available:
            print(f"✅ coolname.com is available!")
            print(f"   Registration: ${availability.pricing.registration}")
            print(f"   Renewal: ${availability.pricing.renewal}")
            print(f"   Transfer: ${availability.pricing.transfer}")

            if availability.first_year_promo:
                print(f"   🎉 First year promo! Regular: ${availability.regular_price}")
        else:
            print("❌ coolname.com is taken")

        if availability.premium:
            print("   ⭐ This is a premium domain")
    ```

### Check Multiple TLDs

=== "Async"

    ```python
    import asyncio
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        base_name = "myawesomebrand"
        tlds = ["com", "net", "org", "io", "dev", "app"]

        for tld in tlds:
            domain = f"{base_name}.{tld}"
            try:
                availability = await piglet.domains.check(domain)
                status = "✅" if availability.available else "❌"
                price = f"${availability.pricing.registration}" if availability.available else "taken"
                print(f"{status} {domain}: {price}")
            except Exception as e:
                print(f"⚠️ {domain}: {e}")

            # Small delay to respect rate limits
            await asyncio.sleep(0.5)
    ```

=== "Sync"

    ```python
    import time
    from oinker import Piglet

    with Piglet() as piglet:
        base_name = "myawesomebrand"
        tlds = ["com", "net", "org", "io", "dev", "app"]

        for tld in tlds:
            domain = f"{base_name}.{tld}"
            try:
                availability = piglet.domains.check(domain)
                status = "✅" if availability.available else "❌"
                price = f"${availability.pricing.registration}" if availability.available else "taken"
                print(f"{status} {domain}: {price}")
            except Exception as e:
                print(f"⚠️ {domain}: {e}")

            # Small delay to respect rate limits
            time.sleep(0.5)
    ```

---

## Glue Records

Glue records are used when you run your own nameservers on subdomains of your domain.

### List Glue Records

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        glue_records = await piglet.domains.get_glue_records("example.com")

        for record in glue_records:
            print(f"Host: {record.host}")
            print(f"  IPv4: {record.ipv4}")
            print(f"  IPv6: {record.ipv6}")
            print("---")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        glue_records = piglet.domains.get_glue_records("example.com")

        for record in glue_records:
            print(f"Host: {record.host}")
            print(f"  IPv4: {record.ipv4}")
            print(f"  IPv6: {record.ipv6}")
            print("---")
    ```

### Create Glue Record

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # IPv4 only
        await piglet.domains.create_glue_record(
            "example.com",
            subdomain="ns1",
            ips=["192.168.1.1"]
        )

        # IPv4 and IPv6
        await piglet.domains.create_glue_record(
            "example.com",
            subdomain="ns2",
            ips=["192.168.1.2", "2001:db8::1"]
        )

        print("Glue records created!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        # IPv4 only
        piglet.domains.create_glue_record(
            "example.com",
            subdomain="ns1",
            ips=["192.168.1.1"]
        )

        # IPv4 and IPv6
        piglet.domains.create_glue_record(
            "example.com",
            subdomain="ns2",
            ips=["192.168.1.2", "2001:db8::1"]
        )

        print("Glue records created!")
    ```

### Update Glue Record

Updates replace all existing IPs with the new list.

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        await piglet.domains.update_glue_record(
            "example.com",
            subdomain="ns1",
            ips=["10.0.0.1", "2001:db8::2"]
        )
        print("Glue record updated!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        piglet.domains.update_glue_record(
            "example.com",
            subdomain="ns1",
            ips=["10.0.0.1", "2001:db8::2"]
        )
        print("Glue record updated!")
    ```

### Delete Glue Record

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        await piglet.domains.delete_glue_record("example.com", subdomain="ns1")
        print("Glue record deleted!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        piglet.domains.delete_glue_record("example.com", subdomain="ns1")
        print("Glue record deleted!")
    ```

---

## Real-World Patterns

### Find Expiring Domains

=== "Async"

    ```python
    from datetime import datetime, timedelta
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        domains = await piglet.domains.list()

        # Find domains expiring in the next 30 days
        threshold = datetime.now() + timedelta(days=30)

        expiring = [
            d for d in domains
            if d.expire_date and d.expire_date < threshold
        ]

        if expiring:
            print("⚠️ Domains expiring soon:")
            for domain in sorted(expiring, key=lambda d: d.expire_date):
                days_left = (domain.expire_date - datetime.now()).days
                print(f"  {domain.domain}: {days_left} days left")
        else:
            print("✅ No domains expiring in the next 30 days")
    ```

=== "Sync"

    ```python
    from datetime import datetime, timedelta
    from oinker import Piglet

    with Piglet() as piglet:
        domains = piglet.domains.list()

        # Find domains expiring in the next 30 days
        threshold = datetime.now() + timedelta(days=30)

        expiring = [
            d for d in domains
            if d.expire_date and d.expire_date < threshold
        ]

        if expiring:
            print("⚠️ Domains expiring soon:")
            for domain in sorted(expiring, key=lambda d: d.expire_date):
                days_left = (domain.expire_date - datetime.now()).days
                print(f"  {domain.domain}: {days_left} days left")
        else:
            print("✅ No domains expiring in the next 30 days")
    ```

### Audit Domain Security Settings

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        domains = await piglet.domains.list()

        print("Security Audit:")
        print("-" * 60)

        for domain in domains:
            issues = []

            if not domain.security_lock:
                issues.append("🔓 Security lock disabled")

            if not domain.whois_privacy:
                issues.append("👁️ WHOIS privacy disabled")

            if not domain.auto_renew:
                issues.append("⏰ Auto-renew disabled")

            if issues:
                print(f"\n{domain.domain}:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print(f"\n{domain.domain}: ✅ All good!")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        domains = piglet.domains.list()

        print("Security Audit:")
        print("-" * 60)

        for domain in domains:
            issues = []

            if not domain.security_lock:
                issues.append("🔓 Security lock disabled")

            if not domain.whois_privacy:
                issues.append("👁️ WHOIS privacy disabled")

            if not domain.auto_renew:
                issues.append("⏰ Auto-renew disabled")

            if issues:
                print(f"\n{domain.domain}:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print(f"\n{domain.domain}: ✅ All good!")
    ```
