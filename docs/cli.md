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

### dns create

Create a new DNS record.

```bash
oinker dns create DOMAIN TYPE [SUBDOMAIN] CONTENT [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `DOMAIN` | Domain name (e.g., `example.com`) |
| `TYPE` | Record type (A, AAAA, MX, TXT, CNAME, etc.) |
| `SUBDOMAIN` | Subdomain (optional, omit for root) |
| `CONTENT` | Record content |

**Options:**

| Option | Description |
|--------|-------------|
| `--ttl` | Time to live in seconds (default: 600) |
| `--priority`, `-p` | Priority for MX/SRV records |
| `--notes` | Notes for the record |

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

### dns delete

Delete a DNS record by ID or by type and name.

```bash
oinker dns delete DOMAIN --id RECORD_ID
oinker dns delete DOMAIN --type TYPE --name SUBDOMAIN
```

**Options:**

| Option | Description |
|--------|-------------|
| `--id`, `-i` | Record ID to delete |
| `--type`, `-t` | Record type (for delete by type/name) |
| `--name`, `-n` | Subdomain name (for delete by type/name, use @ for root) |

**Examples:**

```bash
# Delete by ID
oinker dns delete example.com --id 123456

# Delete all A records for www subdomain
oinker dns delete example.com --type A --name www

# Delete all TXT records at root
oinker dns delete example.com --type TXT --name @
```

Output:

```text
🐷 Gobbled up record 123456
```

## 🌐 Domain Commands

### domains list

List all domains in your account.

```bash
oinker domains list
```

Output:

```text
┌─────────────────┬────────┬────────────┬────────────┬───────────────┐
│ Domain          │ Status │ Expires    │ Auto-Renew │ WHOIS Privacy │
├─────────────────┼────────┼────────────┼────────────┼───────────────┤
│ example.com     │ ACTIVE │ 2025-12-01 │ ✓          │ ✓             │
│ example.org     │ ACTIVE │ 2025-06-15 │            │ ✓             │
└─────────────────┴────────┴────────────┴────────────┴───────────────┘
```

### domains nameservers

Get the authoritative nameservers for a domain.

```bash
oinker domains nameservers DOMAIN
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `DOMAIN` | Domain name (e.g., `example.com`) |

**Example:**

```bash
oinker domains nameservers example.com
```

Output:

```text
🐷 Nameservers for example.com:
   ns1.porkbun.com
   ns2.porkbun.com
```

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
