from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser
from app.database import get_db
from app.models import Outfit
from app.schemas.dto import OutfitCreate, OutfitOut

router = APIRouter()


@router.get("", response_model=list[OutfitOut])
def list_outfits(user: CurrentUser, db: Session = Depends(get_db)):
    return db.query(Outfit).filter(Outfit.user_id == user.id).order_by(Outfit.id.desc()).all()


@router.post("", response_model=OutfitOut, status_code=status.HTTP_201_CREATED)
def create(body: OutfitCreate, user: CurrentUser, db: Session = Depends(get_db)):
    outfit = Outfit(user_id=user.id, **body.model_dump())
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(outfit_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    o = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == user.id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(o)
    db.commit()
    return None
