"""SSL-related type definitions for oinker.

Dataclasses for SSL certificate operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SSLBundle:
    """SSL certificate bundle for a domain.

    Attributes:
        certificate_chain: The complete certificate chain (PEM format).
        private_key: The private key (PEM format).
        public_key: The public key (PEM format).
    """

    certificate_chain: str
    private_key: str
    public_key: str

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> SSLBundle:
        """Create from API response data.

        Args:
            data: The API response dictionary.

        Returns:
            An SSLBundle instance.
        """
        return cls(
            certificate_chain=data.get("certificatechain", ""),
            private_key=data.get("privatekey", ""),
            public_key=data.get("publickey", ""),
        )
