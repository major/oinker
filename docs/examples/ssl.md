# SSL Certificates

This page covers retrieving free SSL certificates from Porkbun.

!!! tip "Free SSL Certificates"
    Porkbun provides free SSL certificates (via Let's Encrypt) for domains using their nameservers. Certificates auto-renew automatically.

## Quick Start

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        bundle = await piglet.ssl.retrieve("example.com")

        print("Certificate retrieved!")
        print(f"Chain length: {len(bundle.certificate_chain)} bytes")
        print(f"Private key length: {len(bundle.private_key)} bytes")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        bundle = piglet.ssl.retrieve("example.com")

        print("Certificate retrieved!")
        print(f"Chain length: {len(bundle.certificate_chain)} bytes")
        print(f"Private key length: {len(bundle.private_key)} bytes")
    ```

---

## Retrieve SSL Bundle

The SSL bundle contains three components:

- **Certificate Chain** - The full certificate chain (your cert + intermediates)
- **Private Key** - The private key for the certificate
- **Public Key** - The public key

=== "Async"

    ```python
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        bundle = await piglet.ssl.retrieve("example.com")

        # Certificate chain (PEM format)
        print("=== Certificate Chain ===")
        print(bundle.certificate_chain[:500] + "...")

        # Private key (PEM format)
        print("\n=== Private Key ===")
        print(bundle.private_key[:100] + "...")

        # Public key (PEM format)
        print("\n=== Public Key ===")
        print(bundle.public_key[:100] + "...")
    ```

=== "Sync"

    ```python
    from oinker import Piglet

    with Piglet() as piglet:
        bundle = piglet.ssl.retrieve("example.com")

        # Certificate chain (PEM format)
        print("=== Certificate Chain ===")
        print(bundle.certificate_chain[:500] + "...")

        # Private key (PEM format)
        print("\n=== Private Key ===")
        print(bundle.private_key[:100] + "...")

        # Public key (PEM format)
        print("\n=== Public Key ===")
        print(bundle.public_key[:100] + "...")
    ```

---

## Save to Files

=== "Async"

    ```python
    from pathlib import Path
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        bundle = await piglet.ssl.retrieve("example.com")

        # Create output directory
        output_dir = Path("/etc/ssl/example.com")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save certificate chain
        cert_path = output_dir / "fullchain.pem"
        cert_path.write_text(bundle.certificate_chain)
        print(f"Saved certificate chain to {cert_path}")

        # Save private key with restricted permissions
        key_path = output_dir / "privkey.pem"
        key_path.write_text(bundle.private_key)
        key_path.chmod(0o600)  # Owner read/write only
        print(f"Saved private key to {key_path}")

        # Save public key (optional)
        pub_path = output_dir / "pubkey.pem"
        pub_path.write_text(bundle.public_key)
        print(f"Saved public key to {pub_path}")
    ```

=== "Sync"

    ```python
    from pathlib import Path
    from oinker import Piglet

    with Piglet() as piglet:
        bundle = piglet.ssl.retrieve("example.com")

        # Create output directory
        output_dir = Path("/etc/ssl/example.com")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save certificate chain
        cert_path = output_dir / "fullchain.pem"
        cert_path.write_text(bundle.certificate_chain)
        print(f"Saved certificate chain to {cert_path}")

        # Save private key with restricted permissions
        key_path = output_dir / "privkey.pem"
        key_path.write_text(bundle.private_key)
        key_path.chmod(0o600)  # Owner read/write only
        print(f"Saved private key to {key_path}")

        # Save public key (optional)
        pub_path = output_dir / "pubkey.pem"
        pub_path.write_text(bundle.public_key)
        print(f"Saved public key to {pub_path}")
    ```

---

## Real-World Patterns

### Deploy to Nginx

=== "Async"

    ```python
    import subprocess
    from pathlib import Path
    from oinker import AsyncPiglet

    async def deploy_ssl_nginx(domain: str) -> None:
        """Fetch SSL cert and deploy to Nginx."""
        async with AsyncPiglet() as piglet:
            bundle = await piglet.ssl.retrieve(domain)

        # Standard Nginx SSL paths
        ssl_dir = Path(f"/etc/nginx/ssl/{domain}")
        ssl_dir.mkdir(parents=True, exist_ok=True)

        # Write certificate files
        (ssl_dir / "fullchain.pem").write_text(bundle.certificate_chain)
        key_path = ssl_dir / "privkey.pem"
        key_path.write_text(bundle.private_key)
        key_path.chmod(0o600)

        # Test Nginx configuration
        result = subprocess.run(
            ["nginx", "-t"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Nginx config error: {result.stderr}")
            return

        # Reload Nginx
        subprocess.run(["systemctl", "reload", "nginx"])
        print(f"✅ SSL certificate deployed for {domain}")

    # Usage
    import asyncio
    asyncio.run(deploy_ssl_nginx("example.com"))
    ```

=== "Sync"

    ```python
    import subprocess
    from pathlib import Path
    from oinker import Piglet

    def deploy_ssl_nginx(domain: str) -> None:
        """Fetch SSL cert and deploy to Nginx."""
        with Piglet() as piglet:
            bundle = piglet.ssl.retrieve(domain)

        # Standard Nginx SSL paths
        ssl_dir = Path(f"/etc/nginx/ssl/{domain}")
        ssl_dir.mkdir(parents=True, exist_ok=True)

        # Write certificate files
        (ssl_dir / "fullchain.pem").write_text(bundle.certificate_chain)
        key_path = ssl_dir / "privkey.pem"
        key_path.write_text(bundle.private_key)
        key_path.chmod(0o600)

        # Test Nginx configuration
        result = subprocess.run(
            ["nginx", "-t"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Nginx config error: {result.stderr}")
            return

        # Reload Nginx
        subprocess.run(["systemctl", "reload", "nginx"])
        print(f"✅ SSL certificate deployed for {domain}")

    # Usage
    deploy_ssl_nginx("example.com")
    ```

### Fetch Certificates for Multiple Domains

=== "Async"

    ```python
    import asyncio
    from pathlib import Path
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        # Get all domains
        domains = await piglet.domains.list()

        output_base = Path("./ssl_certs")
        output_base.mkdir(exist_ok=True)

        for domain_info in domains:
            domain = domain_info.domain
            try:
                bundle = await piglet.ssl.retrieve(domain)

                domain_dir = output_base / domain
                domain_dir.mkdir(exist_ok=True)

                (domain_dir / "fullchain.pem").write_text(bundle.certificate_chain)
                key_path = domain_dir / "privkey.pem"
                key_path.write_text(bundle.private_key)
                key_path.chmod(0o600)

                print(f"✅ {domain}")

            except Exception as e:
                print(f"❌ {domain}: {e}")
    ```

=== "Sync"

    ```python
    from pathlib import Path
    from oinker import Piglet

    with Piglet() as piglet:
        # Get all domains
        domains = piglet.domains.list()

        output_base = Path("./ssl_certs")
        output_base.mkdir(exist_ok=True)

        for domain_info in domains:
            domain = domain_info.domain
            try:
                bundle = piglet.ssl.retrieve(domain)

                domain_dir = output_base / domain
                domain_dir.mkdir(exist_ok=True)

                (domain_dir / "fullchain.pem").write_text(bundle.certificate_chain)
                key_path = domain_dir / "privkey.pem"
                key_path.write_text(bundle.private_key)
                key_path.chmod(0o600)

                print(f"✅ {domain}")

            except Exception as e:
                print(f"❌ {domain}: {e}")
    ```

### Check Certificate Expiration

=== "Async"

    ```python
    from datetime import datetime
    from cryptography import x509
    from oinker import AsyncPiglet

    async with AsyncPiglet() as piglet:
        bundle = await piglet.ssl.retrieve("example.com")

        # Parse the certificate
        cert = x509.load_pem_x509_certificate(
            bundle.certificate_chain.encode()
        )

        # Get expiration info
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        days_left = (not_after - datetime.now(not_after.tzinfo)).days

        print(f"Subject: {cert.subject}")
        print(f"Issuer: {cert.issuer}")
        print(f"Valid from: {not_before}")
        print(f"Valid until: {not_after}")
        print(f"Days remaining: {days_left}")

        if days_left < 30:
            print("⚠️ Certificate expires soon!")
        else:
            print("✅ Certificate is healthy")
    ```

=== "Sync"

    ```python
    from datetime import datetime
    from cryptography import x509
    from oinker import Piglet

    with Piglet() as piglet:
        bundle = piglet.ssl.retrieve("example.com")

        # Parse the certificate
        cert = x509.load_pem_x509_certificate(
            bundle.certificate_chain.encode()
        )

        # Get expiration info
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        days_left = (not_after - datetime.now(not_after.tzinfo)).days

        print(f"Subject: {cert.subject}")
        print(f"Issuer: {cert.issuer}")
        print(f"Valid from: {not_before}")
        print(f"Valid until: {not_after}")
        print(f"Days remaining: {days_left}")

        if days_left < 30:
            print("⚠️ Certificate expires soon!")
        else:
            print("✅ Certificate is healthy")
    ```

!!! note "cryptography library"
    The certificate parsing example requires the `cryptography` library:
    ```bash
    pip install cryptography
    ```
