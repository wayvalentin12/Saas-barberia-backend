from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Negocio
from schemes import NegocioResponse, NegocioCreate

router = APIRouter()

@router.get("/", response_model=List[NegocioResponse])
async def read_negocios(db: Session = Depends(get_db)):
    return db.query(Negocio).all()

@router.get("/{negocio_id}", response_model=NegocioResponse)
async def read_negocio(negocio_id: int, db: Session = Depends(get_db)):
    negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return negocio
@router.put("/{negocio_id}", response_model=NegocioResponse)
async def update_negocio(negocio_id: int, payload: NegocioCreate, db: Session = Depends(get_db)):
    negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    if payload.name is not None:
        negocio.name = payload.name   
    db.commit()
    db.refresh(negocio)
    return negocio