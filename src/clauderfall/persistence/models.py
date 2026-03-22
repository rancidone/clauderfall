"""Relational models for durable artifact storage."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base for relational persistence models."""


class ArtifactRecord(Base):
    """Canonical persisted artifact body plus queryable metadata."""

    __tablename__ = "artifacts"

    artifact_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    artifact_kind: Mapped[str] = mapped_column(String(64), index=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    readiness_state: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    body_json: Mapped[dict] = mapped_column(JSON)
    upstream_artifact_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ArtifactTraceLinkRecord(Base):
    """Trace-link index rows for persisted artifact versions."""

    __tablename__ = "artifact_trace_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(String(128), index=True)
    artifact_kind: Mapped[str] = mapped_column(String(64), index=True)
    version: Mapped[int] = mapped_column(Integer, index=True)
    trace_link: Mapped[str] = mapped_column(String(512), index=True)
    target_ref: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
