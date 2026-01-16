# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - "First Oink" - 2026-01-16

### Added

- **Async client** (`AsyncPiglet`) - Core async Porkbun API client
- **Sync client** (`Piglet`) - Synchronous wrapper for non-async code
- **DNS management** - Full CRUD operations for DNS records
  - Type-safe record dataclasses: `ARecord`, `AAAARecord`, `MXRecord`, `TXTRecord`, `CNAMERecord`, `ALIASRecord`, `NSRecord`, `SRVRecord`, `TLSARecord`, `CAARecord`, `HTTPSRecord`, `SVCBRecord`, `SSHFPRecord`
  - Validation on construction (IP addresses, TTL, priority)
  - Query by ID or by subdomain/type
- **Domain management** - Nameservers, URL forwarding, glue records, availability checks
- **DNSSEC support** - List, create, and delete DNSSEC records
- **SSL certificates** - Retrieve SSL bundles for domains
- **CLI** - Command-line interface with `oinker` command
  - `ping` - Test API connectivity
  - `dns list` - List DNS records
  - `dns create` - Create DNS records
  - `dns delete` - Delete DNS records
- **Exception hierarchy** - Typed exceptions for error handling
  - `AuthenticationError`, `AuthorizationError`, `RateLimitError`, `NotFoundError`, `ValidationError`, `APIError`
- **Auto-retry** - Exponential backoff for transient failures
- **Documentation** - MkDocs with Material theme

[Unreleased]: https://github.com/major/oinker/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/major/oinker/releases/tag/v0.1.0
