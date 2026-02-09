from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas import BorewellCreate, BorewellOut, BorewellUpdateOutcome
from ..ml_models import predict_from_models, MODEL_VERSION
from .auth import get_current_user

from typing import List
router = APIRouter(prefix="/borewells", tags=["borewells"])


@router.post("/", response_model=BorewellOut)
def register_borewell(
    payload: BorewellCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    feasible, depth = predict_from_models(
        lat=payload.latitude,
        lon=payload.longitude,
    )

    borewell = models.Borewell(
        owner_id=current_user.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        predicted_feasible=feasible,
        predicted_depth_m=depth,
        model_version=MODEL_VERSION,
    )
    db.add(borewell)
    db.commit()
    db.refresh(borewell)
    return borewell


@router.patch("/{borewell_id}/outcome", response_model=BorewellOut)
def update_borewell_outcome(
    borewell_id: int,
    payload: BorewellUpdateOutcome,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    borewell = db.query(models.Borewell).filter(models.Borewell.id == borewell_id).first()
    if not borewell:
        raise HTTPException(status_code=404, detail="Borewell not found")

    if borewell.owner_id is not None and borewell.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this borewell")

    borewell.actual_feasible = payload.actual_feasible
    borewell.actual_depth_m = payload.actual_depth_m
    db.commit()
    db.refresh(borewell)
    return borewell



@router.get("/", response_model=List[BorewellOut])
def list_my_borewells(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Borewell)
        .filter(models.Borewell.owner_id == current_user.id)
        .order_by(models.Borewell.id.desc())
        .all()
    )
