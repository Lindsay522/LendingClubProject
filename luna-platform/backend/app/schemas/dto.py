from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


# --- Closet ---
class ClosetItemCreate(BaseModel):
    name: str
    brand: str | None = None
    category: str
    season: str
    style_tags: str | None = None
    price: float | None = None
    link: str | None = None
    notes: str | None = None


class ClosetItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    brand: str | None
    category: str
    season: str
    style_tags: str | None
    price: float | None
    link: str | None
    notes: str | None


# --- Outfits ---
class OutfitCreate(BaseModel):
    name: str
    occasion: str
    weather: str
    mood: str | None = None
    item_ids: list[int] = []


class OutfitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    occasion: str
    weather: str
    mood: str | None
    item_ids: list[Any]


# --- Wellness ---
class SleepCreate(BaseModel):
    log_date: date
    bed_time: str
    wake_time: str
    hours: float


class SportCreate(BaseModel):
    log_date: date
    activity: str
    duration_min: int


class MoodCreate(BaseModel):
    entry_date: date
    energy: str  # low | ok | good | great


class EventCreate(BaseModel):
    event_date: date
    event_time: time | None = None
    title: str
    event_type: str = "default"


class FocusSessionCreate(BaseModel):
    room_type: str
    planned_seconds: int
    completed_seconds: int
    completed: bool
    started_at: datetime
    ended_at: datetime | None = None


class OutfitWornCreate(BaseModel):
    outfit_id: int
    worn_date: date
    notes: str | None = None
