from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Integer, Float, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClosetItem(Base):
    __tablename__ = "closet_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(512))
    brand: Mapped[str | None] = mapped_column(String(256), nullable=True)
    category: Mapped[str] = mapped_column(String(128))
    season: Mapped[str] = mapped_column(String(64))
    style_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    link: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="closet_items")


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(512))
    occasion: Mapped[str] = mapped_column(String(128))
    weather: Mapped[str] = mapped_column(String(64))
    mood: Mapped[str | None] = mapped_column(String(256), nullable=True)
    item_ids: Mapped[list[Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="outfits")
    wear_logs: Mapped[list["OutfitWearLog"]] = relationship("OutfitWearLog", back_populates="outfit", cascade="all, delete-orphan")


class OutfitWearLog(Base):
    __tablename__ = "outfit_wear_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    outfit_id: Mapped[int] = mapped_column(ForeignKey("outfits.id", ondelete="CASCADE"), index=True)
    worn_date: Mapped[date] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    outfit: Mapped["Outfit"] = relationship("Outfit", back_populates="wear_logs")
