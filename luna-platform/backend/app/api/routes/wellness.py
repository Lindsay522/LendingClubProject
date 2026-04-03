from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser
from app.database import get_db
from app.models import SleepLog, SportLog, MoodEntry, CalendarEvent, FocusSession, OutfitWearLog
from app.schemas.dto import SleepCreate, SportCreate, MoodCreate, EventCreate, FocusSessionCreate, OutfitWornCreate

router = APIRouter()


@router.post("/sleep")
def log_sleep(body: SleepCreate, user: CurrentUser, db: Session = Depends(get_db)):
    row = SleepLog(user_id=user.id, **body.model_dump())
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.get("/sleep")
def list_sleep(user: CurrentUser, db: Session = Depends(get_db), limit: int = 30):
    rows = db.query(SleepLog).filter(SleepLog.user_id == user.id).order_by(SleepLog.log_date.desc()).limit(limit).all()
    return [
        {"id": r.id, "log_date": r.log_date.isoformat(), "bed_time": r.bed_time, "wake_time": r.wake_time, "hours": r.hours}
        for r in rows
    ]


@router.post("/sport")
def log_sport(body: SportCreate, user: CurrentUser, db: Session = Depends(get_db)):
    row = SportLog(user_id=user.id, **body.model_dump())
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.get("/sport")
def list_sport(user: CurrentUser, db: Session = Depends(get_db), limit: int = 30):
    rows = db.query(SportLog).filter(SportLog.user_id == user.id).order_by(SportLog.log_date.desc()).limit(limit).all()
    return [
        {"id": r.id, "log_date": r.log_date.isoformat(), "activity": r.activity, "duration_min": r.duration_min}
        for r in rows
    ]


@router.post("/mood")
def log_mood(body: MoodCreate, user: CurrentUser, db: Session = Depends(get_db)):
    row = MoodEntry(user_id=user.id, **body.model_dump())
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.post("/events")
def add_event(body: EventCreate, user: CurrentUser, db: Session = Depends(get_db)):
    row = CalendarEvent(user_id=user.id, **body.model_dump())
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.get("/events")
def list_events(user: CurrentUser, db: Session = Depends(get_db), limit: int = 200):
    rows = db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id).order_by(CalendarEvent.event_date.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "event_date": r.event_date.isoformat(),
            "event_time": r.event_time.isoformat() if r.event_time else None,
            "title": r.title,
            "event_type": r.event_type,
        }
        for r in rows
    ]


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    row = db.query(CalendarEvent).filter(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return None


@router.post("/focus-sessions")
def log_focus(body: FocusSessionCreate, user: CurrentUser, db: Session = Depends(get_db)):
    row = FocusSession(user_id=user.id, **body.model_dump())
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.post("/outfit-worn")
def log_outfit_worn(body: OutfitWornCreate, user: CurrentUser, db: Session = Depends(get_db)):
    row = OutfitWearLog(user_id=user.id, outfit_id=body.outfit_id, worn_date=body.worn_date, notes=body.notes)
    db.add(row)
    db.commit()
    return {"id": row.id}
