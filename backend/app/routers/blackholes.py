from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/v1", tags=["blackholes"])

@router.get("/blackholes", response_model=List[schemas.BlackHoleRead])
def list_blackholes(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return db.query(models.BlackHole).offset(offset).limit(limit).all()

@router.get("/blackholes/{bh_id}", response_model=schemas.BlackHoleRead)
def get_blackhole(bh_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.BlackHole).get(bh_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Black hole not found")
    return obj

@router.post("/blackholes", response_model=schemas.BlackHoleRead, status_code=201)
def create_blackhole(payload: schemas.BlackHoleCreate, db: Session = Depends(get_db)):
    obj = models.BlackHole(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
