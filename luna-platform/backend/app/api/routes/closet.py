from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser
from app.database import get_db
from app.models import ClosetItem
from app.schemas.dto import ClosetItemCreate, ClosetItemOut

router = APIRouter()


@router.get("", response_model=list[ClosetItemOut])
def list_items(user: CurrentUser, db: Session = Depends(get_db)):
    return db.query(ClosetItem).filter(ClosetItem.user_id == user.id).order_by(ClosetItem.id.desc()).all()


@router.post("", response_model=ClosetItemOut, status_code=status.HTTP_201_CREATED)
def create(body: ClosetItemCreate, user: CurrentUser, db: Session = Depends(get_db)):
    item = ClosetItem(user_id=user.id, **body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    item = db.query(ClosetItem).filter(ClosetItem.id == item_id, ClosetItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return None
