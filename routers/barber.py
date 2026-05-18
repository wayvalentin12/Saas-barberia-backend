from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Barber, User
from schemes import BarberCreate, BarberResponse, BarberUpdate
from auth import hash_password, get_current_user
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/", response_model=BarberResponse, status_code=201)
async def create_barber(payload: BarberCreate, db: Session = Depends(get_db)):
    """Create a new barber."""
    barber = Barber(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        negocio_id=payload.negocio_id
    )
    db.add(barber)
    try:
        db.commit()
        db.refresh(barber)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    return barber

@router.get("/", response_model=List[BarberResponse])
async def read_barbers(negocio_id: int = None, db: Session = Depends(get_db)):
    """Retrieve all barbers, optionally filtered by negocio_id."""
    query = db.query(Barber)
    if negocio_id is not None:
        query = query.filter(Barber.negocio_id == negocio_id)
    return query.all()

@router.get("/{barber_id}", response_model=BarberResponse)
async def read_barber(barber_id: int, db: Session = Depends(get_db)):
    """Retrieve a single barber by ID."""
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")
    return barber

@router.put("/{barber_id}", response_model=BarberResponse)
async def update_barber(
    barber_id: int, 
    payload: BarberUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Update a barber's details. Restricted to users from the same business."""
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")
    
    # Permission check: current user must belong to the same business as the barber
    if current_user.negocio_id != barber.negocio_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar este barbero")
    
    if payload.name is not None:
        barber.name = payload.name
    if payload.email is not None:
        barber.email = payload.email
    if payload.password is not None:
        barber.password = hash_password(payload.password)
    if payload.negocio_id is not None:
        barber.negocio_id = payload.negocio_id
        
    try:
        db.commit()
        db.refresh(barber)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
        
    return barber

@router.delete("/{barber_id}")
async def delete_barber(
    barber_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete a barber. Restricted to users from the same business."""
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")
    
    # Permission check: current user must belong to the same business as the barber
    if current_user.negocio_id != barber.negocio_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este barbero")
        
    db.delete(barber)
    db.commit()
    return {"detail": "Barber deleted"}
