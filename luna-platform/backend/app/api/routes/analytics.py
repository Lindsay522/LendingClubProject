from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser
from app.database import get_db
from app.services.analytics_service import build_user_summary, weekly_trends
from app.services.recommendation_service import recommend_focus_block_minutes, recommend_outfits, suggest_plan_nudge

router = APIRouter()


@router.get("/analytics/summary")
def summary(user: CurrentUser, db: Session = Depends(get_db)):
    return build_user_summary(db, user.id)


@router.get("/analytics/trends")
def trends(user: CurrentUser, db: Session = Depends(get_db), weeks: int = 8):
    return weekly_trends(db, user.id, weeks=weeks)


@router.get("/recommendations/outfits")
def rec_outfits(
    user: CurrentUser,
    db: Session = Depends(get_db),
    occasion: str | None = None,
    season: str | None = None,
    limit: int = Query(5, ge=1, le=20),
):
    return {"suggestions": recommend_outfits(db, user.id, occasion=occasion, season_hint=season, limit=limit)}


@router.get("/recommendations/focus")
def rec_focus(user: CurrentUser, db: Session = Depends(get_db)):
    return recommend_focus_block_minutes(db, user.id)


@router.get("/recommendations/plan")
def rec_plan(user: CurrentUser, db: Session = Depends(get_db)):
    return suggest_plan_nudge(db, user.id)
