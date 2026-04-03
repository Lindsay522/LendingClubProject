"""Pandas-backed analytics for portfolio / research narrative."""

from __future__ import annotations

from datetime import date, datetime, time as dtime, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models import SleepLog, SportLog, MoodEntry, FocusSession, OutfitWearLog, Outfit


def _safe_corr(s1: pd.Series, s2: pd.Series) -> float | None:
    if len(s1) < 5 or len(s2) < 5:
        return None
    aligned = pd.concat([s1, s2], axis=1).dropna()
    if len(aligned) < 5:
        return None
    r = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
    if np.isnan(r):
        return None
    return float(r)


def build_user_summary(db: Session, user_id: int) -> dict[str, Any]:
    """Aggregate last 30d behavior for dashboard cards + research plots."""
    start = date.today() - timedelta(days=30)

    sleep_rows = [{"d": r.log_date, "hours": r.hours} for r in db.query(SleepLog).filter(SleepLog.user_id == user_id, SleepLog.log_date >= start).all()]
    sport_rows = [{"d": r.log_date, "minutes": r.duration_min} for r in db.query(SportLog).filter(SportLog.user_id == user_id, SportLog.log_date >= start).all()]
    mood_rows = [{"d": r.entry_date, "energy": r.energy} for r in db.query(MoodEntry).filter(MoodEntry.user_id == user_id, MoodEntry.entry_date >= start).all()]
    start_dt = datetime.combine(start, dtime.min)
    focus_rows = [
        {"d": r.started_at.date(), "completed_sec": r.completed_seconds, "completed": r.completed}
        for r in db.query(FocusSession).filter(FocusSession.user_id == user_id, FocusSession.started_at >= start_dt).all()
    ]
    wear_rows = [{"d": r.worn_date, "outfit_id": r.outfit_id} for r in db.query(OutfitWearLog).filter(OutfitWearLog.user_id == user_id, OutfitWearLog.worn_date >= start).all()]

    out: dict[str, Any] = {
        "window_days": 30,
        "sleep_avg_hours": None,
        "sport_total_minutes": None,
        "focus_completed_sessions": None,
        "corr_sleep_vs_focus_minutes": None,
        "top_outfits_worn": [],
    }

    if sleep_rows:
        sdf = pd.DataFrame(sleep_rows)
        out["sleep_avg_hours"] = round(float(sdf["hours"].mean()), 2)
    if sport_rows:
        spf = pd.DataFrame(sport_rows)
        out["sport_total_minutes"] = int(spf["minutes"].sum())
    if focus_rows:
        fdf = pd.DataFrame(focus_rows)
        out["focus_completed_sessions"] = int(fdf["completed"].sum()) if "completed" in fdf.columns else len(fdf)

    # Merge sleep + focus by day for correlation
    if sleep_rows and focus_rows:
        s_day = pd.DataFrame(sleep_rows).groupby("d")["hours"].mean()
        f_day = pd.DataFrame(focus_rows).groupby("d")["completed_sec"].sum() / 60.0
        out["corr_sleep_vs_focus_minutes"] = _safe_corr(s_day, f_day)

    if wear_rows:
        wdf = pd.DataFrame(wear_rows)
        top = wdf.groupby("outfit_id").size().sort_values(ascending=False).head(5)
        ids = top.index.tolist()
        outfits = {o.id: o.name for o in db.query(Outfit).filter(Outfit.user_id == user_id, Outfit.id.in_(ids)).all()}
        out["top_outfits_worn"] = [{"outfit_id": i, "name": outfits.get(i, str(i)), "count": int(top[i])} for i in ids]

    # Mood distribution (simple counts)
    if mood_rows:
        mdf = pd.DataFrame(mood_rows)
        out["mood_distribution"] = mdf.groupby("energy").size().to_dict()
    else:
        out["mood_distribution"] = {}

    return out


def weekly_trends(db: Session, user_id: int, weeks: int = 8) -> dict[str, Any]:
    start = date.today() - timedelta(weeks=7 * weeks)
    sleep = db.query(SleepLog).filter(SleepLog.user_id == user_id, SleepLog.log_date >= start).all()
    if not sleep:
        return {"series": []}
    sdf = pd.DataFrame([{"week": pd.Timestamp(s.log_date).to_period("W").start_time, "hours": s.hours} for s in sleep])
    g = sdf.groupby("week")["hours"].mean().reset_index()
    g["week"] = g["week"].dt.strftime("%Y-%m-%d")
    return {"metric": "avg_sleep_hours_by_week", "series": g.to_dict(orient="records")}
