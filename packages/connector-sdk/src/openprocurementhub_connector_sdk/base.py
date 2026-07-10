"""Connector plugin contract for procurement sources."""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from openprocurementhub_core.models import Tender
from pydantic import BaseModel, Field, HttpUrl


class RawDocument(BaseModel):
    source: str; source_id: str; url: HttpUrl | None = None; fetched_at: datetime; content: bytes; content_type: str = "application/json"; metadata: dict[str, Any] = Field(default_factory=dict)
class ConnectorCapabilities(BaseModel):
    incremental_sync: bool = True; deduplication: bool = True; attachments: bool = True; supported_formats: list[str] = Field(default_factory=lambda: ["json"]); countries: list[str] = Field(default_factory=list)
class ConnectorHealth(BaseModel):
    healthy: bool; message: str = "ok"; details: dict[str, Any] = Field(default_factory=dict)
class SyncResult(BaseModel):
    connector: str; fetched: int = 0; normalized: int = 0; upserted: int = 0; failed: int = 0; cursor: str | None = None; errors: list[str] = Field(default_factory=list)
class ProcurementConnector(ABC):
    name: str
    @abstractmethod
    async def discover(self) -> list[str]: ...
    @abstractmethod
    async def fetch(self, cursor: str | None = None) -> AsyncIterator[RawDocument]: ...
    @abstractmethod
    async def normalize(self, document: RawDocument) -> Tender: ...
    async def validate(self, tender: Tender) -> Tender: return Tender.model_validate(tender)
    async def sync(self, cursor: str | None = None) -> SyncResult:
        result = SyncResult(connector=self.name, cursor=cursor)
        async for doc in self.fetch(cursor):
            result.fetched += 1
            try:
                await self.validate(await self.normalize(doc)); result.normalized += 1; result.upserted += 1; result.cursor = doc.source_id
            except Exception as exc: result.failed += 1; result.errors.append(f"{doc.source_id}: {exc}")
        return result
    @abstractmethod
    async def health(self) -> ConnectorHealth: ...
    @abstractmethod
    def metadata(self) -> dict[str, Any]: ...
    @abstractmethod
    def capabilities(self) -> ConnectorCapabilities: ...
