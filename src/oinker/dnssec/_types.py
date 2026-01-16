"""DNSSEC-related type definitions for oinker.

Dataclasses for DNSSEC record operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DNSSECRecord:
    """A DNSSEC record from the registry.

    Attributes:
        key_tag: The DNSSEC key tag.
        algorithm: The DS data algorithm.
        digest_type: The digest type.
        digest: The digest value.
    """

    key_tag: str
    algorithm: str
    digest_type: str
    digest: str

    @classmethod
    def from_api_response(cls, key_tag: str, data: dict[str, Any]) -> DNSSECRecord:
        """Create from API response data.

        Args:
            key_tag: The key tag from the response dictionary key.
            data: The record data from API response.

        Returns:
            A DNSSECRecord instance.
        """
        return cls(
            key_tag=data.get("keyTag", key_tag),
            algorithm=data.get("alg", ""),
            digest_type=data.get("digestType", ""),
            digest=data.get("digest", ""),
        )


@dataclass(slots=True)
class DNSSECRecordCreate:
    """Parameters for creating a DNSSEC record.

    Most registries only require the DS data fields (key_tag, algorithm,
    digest_type, digest). The key data fields are optional and vary by registry.

    Attributes:
        key_tag: The DNSSEC key tag.
        algorithm: The DS data algorithm.
        digest_type: The digest type.
        digest: The digest value.
        max_sig_life: Optional max signature life.
        key_data_flags: Optional key data flags.
        key_data_protocol: Optional key data protocol.
        key_data_algorithm: Optional key data algorithm.
        key_data_public_key: Optional key data public key.
    """

    key_tag: str
    algorithm: str
    digest_type: str
    digest: str
    max_sig_life: str | None = None
    key_data_flags: str | None = None
    key_data_protocol: str | None = None
    key_data_algorithm: str | None = None
    key_data_public_key: str | None = None
