# 💰 Pricing

Domain TLD pricing information. This API does not require authentication.

## 🚀 Quick Example

=== "Async"

    ```python
    from oinker.pricing import get_pricing

    # Get pricing for all TLDs
    pricing = await get_pricing()

    # Check .com pricing
    com = pricing["com"]
    print(f".com registration: ${com.registration}")
    print(f".com renewal: ${com.renewal}")
    print(f".com transfer: ${com.transfer}")

    # Find cheapest TLDs
    sorted_by_price = sorted(
        pricing.values(),
        key=lambda p: float(p.registration)
    )
    for tld in sorted_by_price[:5]:
        print(f".{tld.tld}: ${tld.registration}")
    ```

=== "Sync"

    ```python
    from oinker.pricing import get_pricing_sync

    # Get pricing for all TLDs
    pricing = get_pricing_sync()

    # Check .com pricing
    com = pricing["com"]
    print(f".com registration: ${com.registration}")
    print(f".com renewal: ${com.renewal}")
    print(f".com transfer: ${com.transfer}")
    ```

## Functions

### get_pricing

::: oinker.pricing.get_pricing

### get_pricing_sync

::: oinker.pricing.get_pricing_sync

## Types

### TLDPricing

::: oinker.pricing.TLDPricing
