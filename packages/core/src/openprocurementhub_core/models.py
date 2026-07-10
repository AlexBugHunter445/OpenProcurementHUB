"""Canonical versioned procurement domain model.

The model is intentionally source-neutral and serializable so connectors can map
TED, eForms, Belgian federal feeds, OCDS-like data, CSV, JSON, and filesystem
imports into the same contract.
"""
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EntityType(StrEnum):
    TENDER="tender"; NOTICE="notice"; BUYER="buyer"; SUPPLIER="supplier"; AWARD="award"; CONTRACT="contract"

class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow")
    source: str
    source_id: str | None = None
    source_url: HttpUrl | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    checksum: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

class VersionedEntity(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    id: UUID = Field(default_factory=uuid4)
    external_id: str | None = None
    schema_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: Metadata

class Contact(BaseModel):
    name: str | None = None; email: str | None = None; phone: str | None = None; url: HttpUrl | None = None

class Location(BaseModel):
    country: str = "BE"; region: str | None = None; locality: str | None = None; postal_code: str | None = None; nuts_code: str | None = None

class CPV(BaseModel):
    code: str = Field(pattern=r"^\d{8}(-\d)?$"); description: str | None = None

class Money(BaseModel):
    amount: float = Field(ge=0); currency: str = Field(default="EUR", min_length=3, max_length=3)

class Deadline(BaseModel):
    name: str; due_at: datetime; timezone: str = "Europe/Brussels"

class Document(VersionedEntity):
    title: str; document_type: str; url: HttpUrl | None = None; language: str | None = None; checksum: str | None = None

class Attachment(BaseModel):
    filename: str; content_type: str | None = None; size_bytes: int | None = Field(default=None, ge=0); url: HttpUrl | None = None

class Buyer(VersionedEntity):
    name: str; identifier: str | None = None; country: str = "BE"; contact: Contact | None = None; location: Location | None = None

class Supplier(VersionedEntity):
    name: str; identifier: str | None = None; country: str | None = None; contact: Contact | None = None

class Lot(VersionedEntity):
    title: str; description: str | None = None; cpvs: list[CPV] = Field(default_factory=list); estimated_value: Money | None = None

class Notice(VersionedEntity):
    title: str; notice_type: str; published_at: datetime | None = None; documents: list[Document] = Field(default_factory=list)

class Funding(BaseModel):
    programme: str | None = None; source: str | None = None; amount: Money | None = None

class Award(VersionedEntity):
    title: str; supplier_ids: list[UUID] = Field(default_factory=list); value: Money | None = None; awarded_at: datetime | None = None

class Contract(VersionedEntity):
    title: str; award_id: UUID | None = None; value: Money | None = None; signed_at: datetime | None = None; starts_at: datetime | None = None; ends_at: datetime | None = None

class Amendment(BaseModel):
    reason: str; changed_at: datetime = Field(default_factory=lambda: datetime.now(UTC)); changes: dict[str, Any]

class History(BaseModel):
    event_type: str; occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC)); actor: str | None = None; data: dict[str, Any] = Field(default_factory=dict)

class Tender(VersionedEntity):
    title: str
    description: str | None = None
    status: str = "active"
    buyers: list[Buyer] = Field(default_factory=list)
    suppliers: list[Supplier] = Field(default_factory=list)
    notices: list[Notice] = Field(default_factory=list)
    awards: list[Award] = Field(default_factory=list)
    contracts: list[Contract] = Field(default_factory=list)
    lots: list[Lot] = Field(default_factory=list)
    cpvs: list[CPV] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    funding: list[Funding] = Field(default_factory=list)
    deadlines: list[Deadline] = Field(default_factory=list)
    documents: list[Document] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)
    amendments: list[Amendment] = Field(default_factory=list)
    history: list[History] = Field(default_factory=list)

T = TypeVar("T", bound=VersionedEntity)
class Page(BaseModel, Generic[T]):
    items: list[T]; total: int; limit: int; offset: int
