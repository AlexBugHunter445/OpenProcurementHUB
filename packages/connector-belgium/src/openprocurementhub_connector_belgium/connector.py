"""Belgian federal procurement connector.

The connector accepts a configurable JSON endpoint and normalizes records from
Belgian e-Procurement style exports. It is deliberately portal-adapter friendly:
additional Belgian regional portals can subclass and override `record_to_tender`.
"""
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import httpx
from openprocurementhub_connector_sdk import (
    ConnectorCapabilities,
    ConnectorHealth,
    ProcurementConnector,
    RawDocument,
)
from openprocurementhub_core.models import CPV, Buyer, Deadline, Location, Metadata, Tender
from tenacity import retry, stop_after_attempt, wait_exponential


class BelgiumFederalConnector(ProcurementConnector):
    name = "belgium-federal"
    def __init__(self, endpoint: str = "https://publicprocurement.be/api/notices", timeout: float = 30.0) -> None:
        self.endpoint = endpoint; self.timeout = timeout
    async def discover(self) -> list[str]: return [self.endpoint]
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _get(self, cursor: str | None) -> list[dict[str, Any]]:
        params = {"cursor": cursor} if cursor else {}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.endpoint, params=params); response.raise_for_status(); data=response.json()
        return data.get("items", data if isinstance(data, list) else [])
    async def fetch(self, cursor: str | None = None) -> AsyncIterator[RawDocument]:
        for item in await self._get(cursor):
            source_id = str(item.get("id") or item.get("notice_id") or item.get("publication_number"))
            yield RawDocument(source=self.name, source_id=source_id, url=item.get("url"), fetched_at=datetime.now(UTC), content=json.dumps(item).encode(), metadata={"cursor": source_id})
    async def normalize(self, document: RawDocument) -> Tender:
        record=json.loads(document.content.decode())
        return self.record_to_tender(record, document)
    def record_to_tender(self, record: dict[str, Any], document: RawDocument) -> Tender:
        meta=Metadata(source=self.name, source_id=document.source_id, source_url=document.url, raw=record)
        buyers=[Buyer(name=str(record.get("buyer") or record.get("authority") or "Unknown buyer"), identifier=record.get("buyer_id"), metadata=meta)]
        cpvs=[CPV(code=str(c), description=None) for c in record.get("cpv", []) if c]
        deadlines=[]
        if record.get("deadline"):
            deadlines.append(Deadline(name="submission", due_at=datetime.fromisoformat(str(record["deadline"]).replace("Z","+00:00"))))
        return Tender(external_id=document.source_id, title=str(record.get("title") or record.get("name") or "Untitled tender"), description=record.get("description"), status=str(record.get("status") or "active"), buyers=buyers, cpvs=cpvs, locations=[Location(country="BE")], deadlines=deadlines, metadata=meta)
    async def health(self) -> ConnectorHealth:
        try:
            async with httpx.AsyncClient(timeout=5) as client: r=await client.get(self.endpoint); ok=r.status_code < 500
            return ConnectorHealth(healthy=ok, details={"status_code": r.status_code})
        except Exception as exc: return ConnectorHealth(healthy=False, message=str(exc))
    def metadata(self) -> dict[str, Any]: return {"name": self.name, "country": "BE", "maintainer": "OpenProcurementHub"}
    def capabilities(self) -> ConnectorCapabilities: return ConnectorCapabilities(countries=["BE"], supported_formats=["json", "eforms-json"])
