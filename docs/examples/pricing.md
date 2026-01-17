# Pricing

This page covers querying domain TLD pricing. This API does not require authentication.

## Quick Start

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    # Check .com pricing
    com = pricing["com"]
    print(f".com registration: ${com.registration}")
    print(f".com renewal: ${com.renewal}")
    print(f".com transfer: ${com.transfer}")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    # Check .com pricing
    com = pricing["com"]
    print(f".com registration: ${com.registration}")
    print(f".com renewal: ${com.renewal}")
    print(f".com transfer: ${com.transfer}")
    ```

---

## Get All TLD Pricing

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    print(f"Found pricing for {len(pricing)} TLDs")

    # Iterate over all TLDs
    for tld, info in pricing.items():
        print(f".{tld}:")
        print(f"  Registration: ${info.registration}")
        print(f"  Renewal: ${info.renewal}")
        print(f"  Transfer: ${info.transfer}")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    print(f"Found pricing for {len(pricing)} TLDs")

    # Iterate over all TLDs
    for tld, info in pricing.items():
        print(f".{tld}:")
        print(f"  Registration: ${info.registration}")
        print(f"  Renewal: ${info.renewal}")
        print(f"  Transfer: ${info.transfer}")
    ```

---

## Real-World Patterns

### Find Cheapest TLDs

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    # Sort by registration price
    sorted_by_price = sorted(
        pricing.values(),
        key=lambda p: float(p.registration)
    )

    print("Top 10 Cheapest TLDs (Registration):")
    print("-" * 40)

    for tld_info in sorted_by_price[:10]:
        print(f".{tld_info.tld}: ${tld_info.registration}")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    # Sort by registration price
    sorted_by_price = sorted(
        pricing.values(),
        key=lambda p: float(p.registration)
    )

    print("Top 10 Cheapest TLDs (Registration):")
    print("-" * 40)

    for tld_info in sorted_by_price[:10]:
        print(f".{tld_info.tld}: ${tld_info.registration}")
    ```

### Find TLDs Under a Budget

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    budget = 10.00  # $10 max

    affordable = [
        info for info in pricing.values()
        if float(info.registration) <= budget
    ]

    # Sort by price
    affordable.sort(key=lambda p: float(p.registration))

    print(f"TLDs under ${budget}:")
    print("-" * 40)

    for tld_info in affordable:
        print(f".{tld_info.tld}: ${tld_info.registration}")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    budget = 10.00  # $10 max

    affordable = [
        info for info in pricing.values()
        if float(info.registration) <= budget
    ]

    # Sort by price
    affordable.sort(key=lambda p: float(p.registration))

    print(f"TLDs under ${budget}:")
    print("-" * 40)

    for tld_info in affordable:
        print(f".{tld_info.tld}: ${tld_info.registration}")
    ```

### Compare Registration vs Renewal

Find TLDs where renewal is significantly different from registration:

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    # Find TLDs where renewal differs from registration
    different_renewal = []

    for info in pricing.values():
        reg = float(info.registration)
        renew = float(info.renewal)
        diff = renew - reg

        if abs(diff) > 1.00:  # More than $1 difference
            different_renewal.append((info.tld, reg, renew, diff))

    # Sort by difference
    different_renewal.sort(key=lambda x: x[3], reverse=True)

    print("TLDs with Different Renewal Prices:")
    print("-" * 50)
    print(f"{'TLD':<10} {'Register':>10} {'Renewal':>10} {'Diff':>10}")
    print("-" * 50)

    for tld, reg, renew, diff in different_renewal[:20]:
        sign = "+" if diff > 0 else ""
        print(f".{tld:<9} ${reg:>9.2f} ${renew:>9.2f} {sign}${diff:>8.2f}")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    # Find TLDs where renewal differs from registration
    different_renewal = []

    for info in pricing.values():
        reg = float(info.registration)
        renew = float(info.renewal)
        diff = renew - reg

        if abs(diff) > 1.00:  # More than $1 difference
            different_renewal.append((info.tld, reg, renew, diff))

    # Sort by difference
    different_renewal.sort(key=lambda x: x[3], reverse=True)

    print("TLDs with Different Renewal Prices:")
    print("-" * 50)
    print(f"{'TLD':<10} {'Register':>10} {'Renewal':>10} {'Diff':>10}")
    print("-" * 50)

    for tld, reg, renew, diff in different_renewal[:20]:
        sign = "+" if diff > 0 else ""
        print(f".{tld:<9} ${reg:>9.2f} ${renew:>9.2f} {sign}${diff:>8.2f}")
    ```

### Search for Specific TLD Types

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    # Country code TLDs (2 characters)
    cctlds = {
        tld: info for tld, info in pricing.items()
        if len(tld) == 2
    }

    print(f"Found {len(cctlds)} country code TLDs")

    # Tech-related TLDs
    tech_tlds = ["io", "dev", "app", "tech", "codes", "software", "systems"]
    print("\nTech TLD Pricing:")
    for tld in tech_tlds:
        if tld in pricing:
            info = pricing[tld]
            print(f"  .{tld}: ${info.registration}")

    # New gTLDs (longer extensions)
    new_gtlds = {
        tld: info for tld, info in pricing.items()
        if len(tld) > 3
    }

    print(f"\nFound {len(new_gtlds)} new gTLDs")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    # Country code TLDs (2 characters)
    cctlds = {
        tld: info for tld, info in pricing.items()
        if len(tld) == 2
    }

    print(f"Found {len(cctlds)} country code TLDs")

    # Tech-related TLDs
    tech_tlds = ["io", "dev", "app", "tech", "codes", "software", "systems"]
    print("\nTech TLD Pricing:")
    for tld in tech_tlds:
        if tld in pricing:
            info = pricing[tld]
            print(f"  .{tld}: ${info.registration}")

    # New gTLDs (longer extensions)
    new_gtlds = {
        tld: info for tld, info in pricing.items()
        if len(tld) > 3
    }

    print(f"\nFound {len(new_gtlds)} new gTLDs")
    ```

### Export Pricing to CSV

=== "Async"

    ```python
    import csv
    from oinker.pricing import get_pricing

    pricing = await get_pricing()

    with open("porkbun_pricing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TLD", "Registration", "Renewal", "Transfer"])

        for info in sorted(pricing.values(), key=lambda p: p.tld):
            writer.writerow([
                info.tld,
                info.registration,
                info.renewal,
                info.transfer,
            ])

    print(f"Exported {len(pricing)} TLDs to porkbun_pricing.csv")
    ```

=== "Sync"

    ```python
    import csv
    from oinker.pricing import get_pricing_sync

    pricing = get_pricing_sync()

    with open("porkbun_pricing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TLD", "Registration", "Renewal", "Transfer"])

        for info in sorted(pricing.values(), key=lambda p: p.tld):
            writer.writerow([
                info.tld,
                info.registration,
                info.renewal,
                info.transfer,
            ])

    print(f"Exported {len(pricing)} TLDs to porkbun_pricing.csv")
    ```
