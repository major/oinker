# Dynamic DNS

This page shows how to build a complete dynamic DNS (DDNS) updater using Oinker. Perfect for home servers, self-hosting, or any situation where your IP address changes.

## Quick Start

A minimal DDNS updater in just a few lines:

```python
from oinker import Piglet, ARecord

with Piglet() as piglet:
    # Get current public IP from Porkbun
    current_ip = piglet.ping().your_ip

    # Update the DNS record
    piglet.dns.edit_by_name_type(
        "example.com",
        record_type="A",
        subdomain="home",
        content=current_ip
    )
    print(f"Updated home.example.com to {current_ip}")
```

---

## Complete DDNS Script

A production-ready script with caching, logging, and error handling:

```python
#!/usr/bin/env python3
"""Dynamic DNS updater for Porkbun using Oinker.

Updates DNS records only when your IP address changes.
Run via cron or systemd timer.
"""

import argparse
import logging
import sys
from pathlib import Path

from oinker import Piglet, ARecord, OinkerError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_cached_ip(cache_file: Path) -> str | None:
    """Read the last known IP from cache file."""
    if cache_file.exists():
        return cache_file.read_text().strip()
    return None


def save_cached_ip(cache_file: Path, ip: str) -> None:
    """Save the current IP to cache file."""
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(ip)


def update_ddns(
    domain: str,
    subdomain: str,
    cache_file: Path,
    force: bool = False,
) -> bool:
    """Update DDNS record if IP has changed.

    Args:
        domain: The domain name (e.g., "example.com")
        subdomain: The subdomain to update (e.g., "home")
        cache_file: Path to cache the last known IP
        force: Update even if IP hasn't changed

    Returns:
        True if record was updated, False otherwise
    """
    with Piglet() as piglet:
        # Get current public IP from Porkbun
        current_ip = piglet.ping().your_ip
        logger.info(f"Current IP: {current_ip}")

        # Check if IP has changed
        cached_ip = get_cached_ip(cache_file)

        if cached_ip == current_ip and not force:
            logger.info("IP unchanged, skipping update")
            return False

        if cached_ip:
            logger.info(f"IP changed: {cached_ip} -> {current_ip}")

        # Check if record exists
        fqdn = f"{subdomain}.{domain}" if subdomain else domain
        records = piglet.dns.get_by_name_type(
            domain,
            record_type="A",
            subdomain=subdomain if subdomain else None,
        )

        if records:
            # Update existing record
            piglet.dns.edit_by_name_type(
                domain,
                record_type="A",
                subdomain=subdomain if subdomain else None,
                content=current_ip,
            )
            logger.info(f"Updated {fqdn} to {current_ip}")
        else:
            # Create new record
            record_id = piglet.dns.create(
                domain,
                ARecord(
                    content=current_ip,
                    name=subdomain if subdomain else None,
                )
            )
            logger.info(f"Created {fqdn} -> {current_ip} (ID: {record_id})")

        # Cache the new IP
        save_cached_ip(cache_file, current_ip)
        return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dynamic DNS updater for Porkbun"
    )
    parser.add_argument(
        "domain",
        help="Domain name (e.g., example.com)",
    )
    parser.add_argument(
        "subdomain",
        nargs="?",
        default="",
        help="Subdomain to update (e.g., home). Omit for root domain.",
    )
    parser.add_argument(
        "--cache-file",
        type=Path,
        default=Path.home() / ".cache" / "oinker-ddns" / "last_ip",
        help="Path to IP cache file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if IP unchanged",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        updated = update_ddns(
            domain=args.domain,
            subdomain=args.subdomain,
            cache_file=args.cache_file,
            force=args.force,
        )
        return 0 if updated else 0  # Success either way

    except OinkerError as e:
        logger.error(f"API error: {e}")
        return 1

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### Usage

```bash
# Set credentials
export PORKBUN_API_KEY="pk1_..."
export PORKBUN_SECRET_KEY="sk1_..."

# Update home.example.com
python ddns.py example.com home

# Update root domain
python ddns.py example.com

# Force update even if IP unchanged
python ddns.py example.com home --force

# Custom cache location
python ddns.py example.com home --cache-file /var/cache/ddns/ip
```

---

## Cron Setup

Run every 5 minutes:

```bash
# Edit crontab
crontab -e

# Add this line:
*/5 * * * * PORKBUN_API_KEY="pk1_..." PORKBUN_SECRET_KEY="sk1_..." /usr/bin/python3 /path/to/ddns.py example.com home >> /var/log/ddns.log 2>&1
```

---

## Systemd Timer Setup

For more robust scheduling with logging:

### `/etc/systemd/system/oinker-ddns.service`

```ini
[Unit]
Description=Oinker Dynamic DNS Updater
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /opt/ddns/ddns.py example.com home
Environment="PORKBUN_API_KEY=pk1_..."
Environment="PORKBUN_SECRET_KEY=sk1_..."

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/cache/oinker-ddns

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/oinker-ddns.timer`

```ini
[Unit]
Description=Run Oinker DDNS every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
AccuracySec=1min

[Install]
WantedBy=timers.target
```

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now oinker-ddns.timer

# Check status
sudo systemctl status oinker-ddns.timer
sudo journalctl -u oinker-ddns.service
```

---

## IPv6 Support

Update both A and AAAA records:

```python
import socket
from oinker import Piglet, ARecord, AAAARecord

def get_ipv6() -> str | None:
    """Get the public IPv6 address."""
    try:
        # Connect to a public IPv6 address to determine our address
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(("2001:4860:4860::8888", 80))  # Google DNS
        ipv6 = s.getsockname()[0]
        s.close()
        return ipv6
    except OSError:
        return None


with Piglet() as piglet:
    domain = "example.com"
    subdomain = "home"

    # Update IPv4 (A record)
    ipv4 = piglet.ping().your_ip
    piglet.dns.edit_by_name_type(
        domain,
        record_type="A",
        subdomain=subdomain,
        content=ipv4,
    )
    print(f"Updated A record: {ipv4}")

    # Update IPv6 (AAAA record) if available
    ipv6 = get_ipv6()
    if ipv6:
        piglet.dns.edit_by_name_type(
            domain,
            record_type="AAAA",
            subdomain=subdomain,
            content=ipv6,
        )
        print(f"Updated AAAA record: {ipv6}")
    else:
        print("No IPv6 address available")
```

---

## Multiple Subdomains

Update multiple subdomains at once:

```python
from oinker import Piglet

DOMAIN = "example.com"
SUBDOMAINS = ["home", "vpn", "nas", "plex"]

with Piglet() as piglet:
    current_ip = piglet.ping().your_ip
    print(f"Current IP: {current_ip}")

    for subdomain in SUBDOMAINS:
        try:
            piglet.dns.edit_by_name_type(
                DOMAIN,
                record_type="A",
                subdomain=subdomain,
                content=current_ip,
            )
            print(f"  ✅ {subdomain}.{DOMAIN}")
        except Exception as e:
            print(f"  ❌ {subdomain}.{DOMAIN}: {e}")
```

---

## Async Version

For concurrent updates or integration with async applications:

```python
import asyncio
from oinker import AsyncPiglet

DOMAIN = "example.com"
SUBDOMAINS = ["home", "vpn", "nas", "plex"]


async def update_all():
    async with AsyncPiglet() as piglet:
        current_ip = (await piglet.ping()).your_ip
        print(f"Current IP: {current_ip}")

        # Update all subdomains concurrently
        tasks = [
            piglet.dns.edit_by_name_type(
                DOMAIN,
                record_type="A",
                subdomain=subdomain,
                content=current_ip,
            )
            for subdomain in SUBDOMAINS
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for subdomain, result in zip(SUBDOMAINS, results):
            if isinstance(result, Exception):
                print(f"  ❌ {subdomain}.{DOMAIN}: {result}")
            else:
                print(f"  ✅ {subdomain}.{DOMAIN}")


asyncio.run(update_all())
```

---

## Notifications

Add notifications when IP changes:

```python
import smtplib
from email.message import EmailMessage
from oinker import Piglet


def send_notification(old_ip: str, new_ip: str, domain: str):
    """Send email notification when IP changes."""
    msg = EmailMessage()
    msg["Subject"] = f"DDNS Update: {domain}"
    msg["From"] = "ddns@example.com"
    msg["To"] = "admin@example.com"
    msg.set_content(f"""
Your dynamic DNS has been updated.

Domain: {domain}
Old IP: {old_ip}
New IP: {new_ip}

This is an automated message from your DDNS updater.
    """)

    with smtplib.SMTP("localhost") as smtp:
        smtp.send_message(msg)


def update_with_notification(domain: str, subdomain: str, cached_ip: str | None):
    with Piglet() as piglet:
        current_ip = piglet.ping().your_ip

        if cached_ip and cached_ip != current_ip:
            # IP changed - update and notify
            piglet.dns.edit_by_name_type(
                domain,
                record_type="A",
                subdomain=subdomain,
                content=current_ip,
            )

            fqdn = f"{subdomain}.{domain}" if subdomain else domain
            send_notification(cached_ip, current_ip, fqdn)
            print(f"Updated and notified: {cached_ip} -> {current_ip}")

        return current_ip
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN pip install oinker

COPY ddns.py .

CMD ["python", "ddns.py"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  ddns:
    build: .
    environment:
      - PORKBUN_API_KEY=${PORKBUN_API_KEY}
      - PORKBUN_SECRET_KEY=${PORKBUN_SECRET_KEY}
    command: ["python", "ddns.py", "example.com", "home"]
    volumes:
      - ddns-cache:/var/cache/ddns
    restart: unless-stopped

volumes:
  ddns-cache:
```

### Run with Docker Compose

```bash
# Create .env file
echo "PORKBUN_API_KEY=pk1_..." > .env
echo "PORKBUN_SECRET_KEY=sk1_..." >> .env

# Run once
docker-compose run --rm ddns

# Run as a service (with external scheduler)
docker-compose up -d
```

For continuous operation, use a scheduler like `ofelia` or run via cron on the host.
