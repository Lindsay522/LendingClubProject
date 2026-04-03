"""Rule-based + scoring recommendations. Upgrade path: sklearn / learned weights."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models import ClosetItem, Outfit, OutfitWearLog


ENERGY_RANK = {"low": 0, "ok": 1, "good": 2, "great": 3}


def recommend_outfits(
    db: Session,
    user_id: int,
    occasion: str | None = None,
    season_hint: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    outfits = db.query(Outfit).filter(Outfit.user_id == user_id).all()
    if not outfits:
        return []

    since = date.today() - timedelta(days=30)
    wear_counts = Counter(r.outfit_id for r in db.query(OutfitWearLog).filter(OutfitWearLog.user_id == user_id, OutfitWearLog.worn_date >= since).all())

    closet = {c.id: c for c in db.query(ClosetItem).filter(ClosetItem.user_id == user_id).all()}
    results: list[tuple[float, Outfit, list[str]]] = []

    for o in outfits:
        reasons: list[str] = []
        score = 0.2

        if occasion and occasion.lower() in (o.occasion or "").lower():
            score += 0.35
            reasons.append(f"Occasion match ({o.occasion})")

        if season_hint and season_hint.lower() in (o.weather or "").lower():
            score += 0.15
            reasons.append("Season / weather hint aligned")

        worn_n = wear_counts.get(o.id, 0)
        if worn_n == 0:
            score += 0.15
            reasons.append("Not worn recently — fresh pick")
        elif worn_n >= 5:
            score -= 0.1
            reasons.append("Worn often lately — lower priority")

        # Tag overlap: outfit mood vs closet tags (weak signal)
        tags_all = []
        for iid in o.item_ids or []:
            c = closet.get(int(iid))
            if c and c.style_tags:
                tags_all.extend([t.strip() for t in c.style_tags.split(",") if t.strip()])
        if tags_all:
            score += min(0.15, 0.02 * len(set(tags_all)))
            reasons.append("Style tags available for cohesion")

        score = max(0.0, min(1.0, score))
        results.append((score, o, reasons))

    results.sort(key=lambda x: -x[0])
    out: list[dict[str, Any]] = []
    for score, o, reasons in results[:limit]:
        out.append(
            {
                "outfit_id": o.id,
                "name": o.name,
                "score": round(score, 3),
                "reasons": reasons,
            }
        )
    return out


def recommend_focus_block_minutes(db: Session, user_id: int) -> dict[str, Any]:
    """Suggest focus length from recent mood + sleep proxy (extend with FocusSession stats)."""
    from app.models import MoodEntry, SleepLog

    moods = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).order_by(MoodEntry.entry_date.desc()).limit(14).all()
    sleeps = db.query(SleepLog).filter(SleepLog.user_id == user_id).order_by(SleepLog.log_date.desc()).limit(7).all()

    if not moods and not sleeps:
        return {"suggested_minutes": 25, "rationale": "Default Pomodoro; log mood/sleep to personalize."}

    avg_sleep = sum(s.hours for s in sleeps) / len(sleeps) if sleeps else 7.0
    last_mood = moods[0].energy if moods else "ok"
    rank = ENERGY_RANK.get(last_mood, 1)

    if avg_sleep < 6.5:
        base = 15
        rationale = "Recent sleep on the lighter side — shorter focus blocks with breaks."
    elif rank >= ENERGY_RANK["good"]:
        base = 35
        rationale = "Recent mood trend positive — slightly longer deep-focus window is reasonable."
    else:
        base = 25
        rationale = "Balanced default; tune with more wellness logs."

    return {"suggested_minutes": base, "rationale": rationale, "signals": {"avg_sleep_7d": round(avg_sleep, 2), "last_mood": last_mood}}


def suggest_plan_nudge(db: Session, user_id: int) -> dict[str, Any]:
    from app.models import CalendarEvent
    from sqlalchemy import func

    rows = db.query(CalendarEvent.event_date, func.count()).filter(CalendarEvent.user_id == user_id).group_by(CalendarEvent.event_date).all()
    if len(rows) < 3:
        return {"nudge": "Keep logging events — we will spot busy vs light days soon.", "busy_days_per_week_estimate": None}

    # crude: count days with >=3 events as "heavy"
    heavy = sum(1 for _, c in rows if c >= 3)
    return {
        "nudge": "On heavy planning days, consider one fewer optional block and a short focus reset.",
        "heavy_day_sample": int(heavy),
    }
