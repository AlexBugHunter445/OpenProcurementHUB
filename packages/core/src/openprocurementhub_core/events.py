"""Internal event bus abstractions."""
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(StrEnum):
    CONNECTOR_SYNCED="connector.synced"; TENDER_CREATED="tender.created"; TENDER_UPDATED="tender.updated"; TENDER_EXPIRED="tender.expired"; CONTRACT_AWARDED="contract.awarded"; WEBHOOK_TRIGGERED="webhook.triggered"
class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4); type: EventType; occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC)); payload: dict[str, Any] = Field(default_factory=dict)
Handler = Callable[[Event], None]
class InMemoryEventBus:
    def __init__(self) -> None: self._handlers: dict[EventType, list[Handler]] = {}
    def subscribe(self, event_type: EventType, handler: Handler) -> None: self._handlers.setdefault(event_type, []).append(handler)
    def publish(self, event: Event) -> None:
        for handler in self._handlers.get(event.type, []): handler(event)
