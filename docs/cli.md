# 💻 CLI Reference

Oinker includes a command-line interface for managing DNS records.

## 📦 Installation

The CLI requires optional dependencies:

```bash
pip install "oinker[cli]"
```

## 🔑 Authentication

Set your credentials as environment variables:

```bash
export PORKBUN_API_KEY="pk1_..."
export PORKBUN_SECRET_KEY="sk1_..."
```

Or pass them with each command:

```bash
oinker --api-key "pk1_..." --secret-key "sk1_..." ping
```

## 🐷 Commands

### ping

Test API connectivity and authentication.

```bash
oinker ping
```

Output:

```text
🐷 Oink! Connected successfully.
   Your IP: 203.0.113.42
```

---

## 📋 DNS Commands

### dns list

List all DNS records for a domain.

```bash
oinker dns list example.com
```

Output:

```text
┌────────┬─────────────────┬──────┬───────────┬─────┐
│ ID     │ Name            │ Type │ Content   │ TTL │
├────────┼─────────────────┼──────┼───────────┼─────┤
│ 123456 │ example.com     │ A    │ 1.2.3.4   │ 600 │
│ 123457 │ www.example.com │ A    │ 1.2.3.4   │ 600 │
└────────┴─────────────────┴──────┴───────────┴─────┘
```

### dns get

Get a specific DNS record by ID or by type/name.

```bash
# Get by ID
oinker dns get example.com --id 123456

# Get by type and name
oinker dns get example.com --type A --name www
```

### dns create

Create a new DNS record.

```bash
oinker dns create DOMAIN TYPE NAME CONTENT [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `DOMAIN` | Domain name (e.g., `example.com`) |
| `TYPE` | Record type (A, AAAA, MX, TXT, CNAME, etc.) |
| `NAME` | Subdomain (use `@` for root) |
| `CONTENT` | Record content |

**Options:**

| Option | Description |
|--------|-------------|
| `--ttl` | Time to live in seconds (default: 600) |
| `--priority`, `-p` | Priority for MX/SRV records |

**Examples:**

```bash
# A record for www subdomain
oinker dns create example.com A www 1.2.3.4

# A record for root domain
oinker dns create example.com A @ 1.2.3.4

# MX record with priority
oinker dns create example.com MX @ mail.example.com --priority 10

# TXT record
oinker dns create example.com TXT @ "v=spf1 include:_spf.google.com ~all"

# CNAME record
oinker dns create example.com CNAME blog www.blogger.com
```

Output:

```text
🐷 Squeee! Created record 123458
```

### dns edit

Edit a DNS record by ID or by type/name.

```bash
# Edit by ID
oinker dns edit example.com --id 123456 --content 1.2.3.5

# Edit by type/name (updates ALL matching records)
oinker dns edit example.com --type A --name www --content 1.2.3.5

# Edit with TTL and notes
oinker dns edit example.com --id 123456 --content 1.2.3.5 --ttl 3600 --notes "Production server"
```

### dns delete

Delete a DNS record by ID or by type/name.

```bash
# Delete by ID
oinker dns delete example.com --id 123456

# Delete by type and name (deletes ALL matching records)
oinker dns delete example.com --type A --name www
```

Output:

```text
🐷 Gobbled up record 123456
```

---

## 🌐 Domain Commands

### domains list

List all domains in your account.

```bash
oinker domains list
```

### domains nameservers

Get authoritative nameservers for a domain.

```bash
oinker domains nameservers example.com
```

### domains update-nameservers

Update the nameservers for a domain.

```bash
oinker domains update-nameservers example.com ns1.example.com ns2.example.com
```

### domains check

Check if a domain is available for registration (rate limited).

```bash
oinker domains check coolname.com
```

Output:

```text
🐷 coolname.com is available!
┌──────────────┬────────┬───────────────┐
│ Type         │ Price  │ Regular Price │
├──────────────┼────────┼───────────────┤
│ Registration │ $9.68  │ $9.68         │
│ Renewal      │ $9.68  │ $9.68         │
│ Transfer     │ $9.68  │ $9.68         │
└──────────────┴────────┴───────────────┘
```

### domains forwards-list

List URL forwarding rules for a domain.

```bash
oinker domains forwards-list example.com
```

### domains forwards-add

Add a URL forwarding rule.

```bash
# Forward root domain
oinker domains forwards-add example.com https://newsite.com

# Forward subdomain
oinker domains forwards-add example.com https://blog.com --subdomain blog

# Permanent redirect with wildcard
oinker domains forwards-add example.com https://newsite.com --type permanent --wildcard
```

**Options:**

| Option | Description |
|--------|-------------|
| `--subdomain`, `-n` | Subdomain to forward (omit for root) |
| `--type`, `-t` | `temporary` (302) or `permanent` (301) |
| `--include-path`, `-p` | Include URI path in redirect |
| `--wildcard`, `-w` | Forward all subdomains |

### domains forwards-delete

Delete a URL forwarding rule.

```bash
oinker domains forwards-delete example.com 12345678
```

### domains glue-list

List glue records for a domain.

```bash
oinker domains glue-list example.com
```

### domains glue-create

Create a glue record.

```bash
# Single IP
oinker domains glue-create example.com ns1 192.168.1.1

# IPv4 and IPv6
oinker domains glue-create example.com ns1 192.168.1.1 2001:db8::1
```

### domains glue-update

Update a glue record (replaces all IPs).

```bash
oinker domains glue-update example.com ns1 192.168.1.2
```

### domains glue-delete

Delete a glue record.

```bash
oinker domains glue-delete example.com ns1
```

---

## 🔐 DNSSEC Commands

### dnssec list

List DNSSEC records for a domain.

```bash
oinker dnssec list example.com
```

### dnssec create

Create a DNSSEC record at the registry.

```bash
oinker dnssec create example.com 64087 13 2 15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `DOMAIN` | Domain name |
| `KEY_TAG` | Key tag (e.g., `64087`) |
| `ALGORITHM` | DS algorithm (e.g., `13` for ECDSAP256SHA256) |
| `DIGEST_TYPE` | Digest type (e.g., `2` for SHA-256) |
| `DIGEST` | Digest value (hex string) |

**Optional key data options:**

| Option | Description |
|--------|-------------|
| `--max-sig-life` | Max signature life |
| `--key-data-flags` | Key data flags |
| `--key-data-protocol` | Key data protocol |
| `--key-data-algorithm` | Key data algorithm |
| `--key-data-public-key` | Key data public key |

### dnssec delete

Delete a DNSSEC record from the registry.

```bash
oinker dnssec delete example.com 64087
```

---

## 🔒 SSL Commands

### ssl retrieve

Retrieve SSL certificate bundle for a domain.

```bash
# Display certificate (without private key)
oinker ssl retrieve example.com

# Save to files
oinker ssl retrieve example.com --output /etc/ssl/certs/
```

When using `--output`, creates three files:

- `domain.crt` - Certificate chain
- `domain.key` - Private key (mode 600)
- `domain.pub` - Public key

---

## 💰 Pricing Commands

### pricing list

List domain pricing for all TLDs (no authentication required).

```bash
# List all TLDs
oinker pricing list

# Filter by TLD
oinker pricing list --tld com

# Sort by price
oinker pricing list --sort registration --limit 20
```

**Options:**

| Option | Description |
|--------|-------------|
| `--tld`, `-t` | Filter by specific TLD |
| `--sort`, `-s` | Sort by: `tld`, `registration`, `renewal`, `transfer` |
| `--limit`, `-l` | Limit number of results |

---

## ⚙️ Common Options

These options are available on each command:

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `--api-key`, `-k` | `PORKBUN_API_KEY` | Porkbun API key |
| `--secret-key`, `-s` | `PORKBUN_SECRET_KEY` | Porkbun secret key |

## 🚦 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (authentication, validation, API error) |

## 🐚 Shell Completion

Generate shell completions for your shell:

```bash
# Bash
oinker --install-completion bash

# Zsh
oinker --install-completion zsh

# Fish
oinker --install-completion fish
```
