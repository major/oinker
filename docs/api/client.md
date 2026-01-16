# 🐷 Client

The main entry points for the Oinker library.

## AsyncPiglet

The async client for the Porkbun API. Use this for async applications.

::: oinker.AsyncPiglet
    options:
      members:
        - __init__
        - ping
        - dns
        - domains
        - dnssec
        - ssl

## Piglet

The sync client, wrapping AsyncPiglet for synchronous code.

::: oinker.Piglet
    options:
      members:
        - __init__
        - ping
        - dns
        - domains
        - dnssec
        - ssl
        - close

## PingResponse

::: oinker.PingResponse
