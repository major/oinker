"""Async DNSSEC API operations for the Porkbun API.

Provides DNSSEC record management operations at the registry level.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from oinker.dnssec._types import DNSSECRecord, DNSSECRecordCreate

if TYPE_CHECKING:
    from oinker._http import HttpClient


class AsyncDNSSECAPI:
    """Async DNSSEC operations for the Porkbun API.

    Accessed via `piglet.dnssec.*` methods.
    """

    def __init__(self, http: HttpClient) -> None:
        """Initialize DNSSEC API.

        Args:
            http: The HTTP client for making requests.
        """
        self._http = http

    async def list(self, domain: str) -> builtins.list[DNSSECRecord]:
        """Get DNSSEC records for a domain from the registry.

        Args:
            domain: The domain name (e.g., "example.com").

        Returns:
            List of DNSSEC records.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        data = await self._http.post(f"/dns/getDnssecRecords/{domain}")
        records_dict = data.get("records", {})
        records: builtins.list[DNSSECRecord] = []
        for key_tag, record_data in records_dict.items():
            records.append(DNSSECRecord.from_api_response(key_tag, record_data))
        return records

    async def create(self, domain: str, record: DNSSECRecordCreate) -> None:
        """Create a DNSSEC record at the registry.

        Note: DNSSEC creation differs at various registries. Most often only
        the DS data fields (key_tag, algorithm, digest_type, digest) are required.

        Args:
            domain: The domain name.
            record: The DNSSEC record to create.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain is not found.
            APIError: If the request fails.
        """
        body: dict[str, Any] = {
            "keyTag": record.key_tag,
            "alg": record.algorithm,
            "digestType": record.digest_type,
            "digest": record.digest,
        }

        if record.max_sig_life is not None:
            body["maxSigLife"] = record.max_sig_life
        if record.key_data_flags is not None:
            body["keyDataFlags"] = record.key_data_flags
        if record.key_data_protocol is not None:
            body["keyDataProtocol"] = record.key_data_protocol
        if record.key_data_algorithm is not None:
            body["keyDataAlgo"] = record.key_data_algorithm
        if record.key_data_public_key is not None:
            body["keyDataPubKey"] = record.key_data_public_key

        await self._http.post(f"/dns/createDnssecRecord/{domain}", body)

    async def delete(self, domain: str, key_tag: str) -> None:
        """Delete a DNSSEC record from the registry.

        Note: Most registries will delete all records with matching data,
        not just the record with the matching key tag.

        Args:
            domain: The domain name.
            key_tag: The key tag of the record to delete.

        Raises:
            AuthenticationError: If credentials are invalid.
            NotFoundError: If domain or record is not found.
            APIError: If the request fails.
        """
        await self._http.post(f"/dns/deleteDnssecRecord/{domain}/{key_tag}")
