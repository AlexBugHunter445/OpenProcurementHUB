"""SQLAlchemy schema for durable procurement storage."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): pass
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), server_default=func.now())
class TenderRecord(Base, TimestampMixin):
    __tablename__="tenders"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(1000), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    __table_args__=(UniqueConstraint("source","external_id", name="uq_tender_source_external"), Index("ix_tenders_payload_gin", "payload", postgresql_using="gin"),)
class ConnectorState(Base, TimestampMixin):
    __tablename__="connector_state"
    name: Mapped[str] = mapped_column(String(128), primary_key=True)
    cursor: Mapped[str | None] = mapped_column(String(1000))
    state: Mapped[dict] = mapped_column(JSONB, default=dict)
class JobRecord(Base, TimestampMixin):
    __tablename__="jobs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connector: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    error: Mapped[str | None] = mapped_column(Text)
class EventRecord(Base, TimestampMixin):
    __tablename__="events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
class WebhookSubscription(Base, TimestampMixin):
    __tablename__="webhook_subscriptions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(String(2000))
    secret: Mapped[str] = mapped_column(String(255))
    events: Mapped[list[str]] = mapped_column(JSONB, default=list)
