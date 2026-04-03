from datetime import date, datetime, time
from typing import Any

from sqlalchemy import String, Text, Date, Time, DateTime, ForeignKey, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_date: Mapped[date] = mapped_column(Date, index=True)
    event_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    title: Mapped[str] = mapped_column(String(512))
    event_type: Mapped[str] = mapped_column(String(64), default="default")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    log_date: Mapped[date] = mapped_column(Date, index=True)
    bed_time: Mapped[str] = mapped_column(String(8))  # HH:MM
    wake_time: Mapped[str] = mapped_column(String(8))
    hours: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SportLog(Base):
    __tablename__ = "sport_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    log_date: Mapped[date] = mapped_column(Date, index=True)
    activity: Mapped[str] = mapped_column(String(128))
    duration_min: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    energy: Mapped[str] = mapped_column(String(16))  # low | ok | good | great
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    room_type: Mapped[str] = mapped_column(String(64))
    planned_seconds: Mapped[int] = mapped_column(Integer)
    completed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
