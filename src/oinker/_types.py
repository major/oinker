"""Shared type definitions for oinker."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PingResponse:
    """Response from the ping endpoint.

    Attributes:
        your_ip: The client's public IP address as seen by Porkbun.
    """

    your_ip: str
